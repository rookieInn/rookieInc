#!/usr/bin/env python3
"""
Email keyword-based auto responder.

This script connects to an IMAP inbox, scans unread messages for configured
keywords, and sends automatic replies through SMTP when matches are found.

Configuration is loaded from a JSON file. See
`email_auto_responder_config.example.json` for the supported options.
"""

from __future__ import annotations

import argparse
import email
import json
import logging
import os
import re
import signal
import smtplib
import ssl
import sys
import time
from dataclasses import dataclass, field
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import formataddr, make_msgid, parseaddr
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import imaplib

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def decode_mime_words(value: str) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:  # pragma: no cover - defensive
        logger.debug("Failed to decode header, returning raw value", exc_info=True)
        return value


def extract_text_from_email(msg: email.message.Message) -> Tuple[str, str]:
    subject = decode_mime_words(msg.get("Subject", ""))

    def iter_text_parts(message: email.message.Message) -> Iterable[Tuple[str, str]]:
        if message.is_multipart():
            for part in message.walk():
                if part.is_multipart():
                    continue
                content_type = part.get_content_type()
                if content_type not in ("text/plain", "text/html"):
                    continue
                charset = part.get_content_charset() or "utf-8"
                try:
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    text = payload.decode(charset, errors="replace")
                except LookupError:
                    text = part.get_payload(decode=True).decode("utf-8", errors="replace")
                yield content_type, text
        else:
            content_type = msg.get_content_type()
            charset = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            if payload:
                try:
                    text = payload.decode(charset, errors="replace")
                except LookupError:
                    text = payload.decode("utf-8", errors="replace")
                yield content_type, text

    body_text = ""
    for content_type, text in iter_text_parts(msg):
        if content_type == "text/plain":
            body_text = text
            break
        if not body_text and content_type == "text/html":
            body_text = strip_html(text)

    return subject, body_text


def strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html, flags=re.S)
    html = re.sub(r"(?s)<br\s*/?>", "\n", html)
    html = re.sub(r"(?s)</p>", "\n", html)
    text = re.sub(r"(?s)<.*?>", "", html)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_json_config(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fh:
        raw_config = json.load(fh)
    return resolve_env_placeholders(raw_config)


def resolve_env_placeholders(obj):
    if isinstance(obj, dict):
        return {key: resolve_env_placeholders(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [resolve_env_placeholders(item) for item in obj]
    if isinstance(obj, str) and obj.startswith("$ENV{") and obj.endswith("}"):
        env_name = obj[5:-1]
        return os.environ.get(env_name, "")
    return obj


@dataclass
class ResponseTemplate:
    subject: str
    body: str
    reply_to_all: bool = False
    include_original_message: bool = False


@dataclass
class KeywordRule:
    name: str
    keywords: Sequence[str]
    response: ResponseTemplate
    match_all: bool = False
    case_sensitive: bool = False

    def matches(self, text: str) -> Optional[str]:
        haystack = text if self.case_sensitive else text.lower()
        keywords = self.keywords if self.case_sensitive else [k.lower() for k in self.keywords]

        if self.match_all:
            if all(keyword in haystack for keyword in keywords):
                return self.keywords[0] if self.keywords else ""
            return None

        for keyword, raw_keyword in zip(keywords, self.keywords):
            if keyword in haystack:
                return raw_keyword
        return None


@dataclass
class AutoResponderConfig:
    imap_host: str
    imap_port: int = 993
    imap_use_ssl: bool = True
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_use_ssl: bool = True
    smtp_use_starttls: bool = False
    username: str = ""
    sender_name: Optional[str] = None
    password: str = ""
    mailbox: str = "INBOX"
    keyword_rules: List[KeywordRule] = field(default_factory=list)
    default_response: Optional[ResponseTemplate] = None
    poll_interval: int = 60
    processed_store: Path = Path(".auto_responder_processed.json")
    max_replies_per_run: Optional[int] = None


class ProcessedMessageStore:
    def __init__(self, path: Path):
        self.path = path
        self._messages = self._load()

    def _load(self) -> Dict[str, float]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return {str(k): float(v) for k, v in data.items()}
        except Exception:
            logger.warning("Failed to load processed message store; starting fresh.", exc_info=True)
        return {}

    def add(self, uid: str) -> None:
        self._messages[str(uid)] = time.time()
        self._save()

    def contains(self, uid: str) -> bool:
        return str(uid) in self._messages

    def _save(self) -> None:
        try:
            with self.path.open("w", encoding="utf-8") as fh:
                json.dump(self._messages, fh, indent=2, ensure_ascii=False)
        except Exception:
            logger.error("Failed to persist processed message store.", exc_info=True)


class KeywordResponder:
    def __init__(self, rules: Sequence[KeywordRule], default_response: Optional[ResponseTemplate]):
        self.rules = list(rules)
        self.default_response = default_response

    def match(self, subject: str, body: str) -> Optional[Tuple[ResponseTemplate, KeywordRule, str]]:
        text = f"{subject}\n{body}".strip()
        for rule in self.rules:
            matched_keyword = rule.matches(text)
            if matched_keyword is not None:
                return rule.response, rule, matched_keyword
        if self.default_response:
            return self.default_response, None, ""
        return None


class EmailAutoResponder:
    def __init__(self, config: AutoResponderConfig):
        self.config = config
        self.responder = KeywordResponder(config.keyword_rules, config.default_response)
        self.processed_store = ProcessedMessageStore(config.processed_store)
        self._should_stop = False

    def run(self, loop: bool = False) -> None:
        def stop_handler(signum, frame):  # pragma: no cover - signal handler
            logger.info("Signal %s received; stopping after current cycle.", signum)
            self._should_stop = True

        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)

        total_replies = 0
        while True:
            processed = self._process_inbox()
            total_replies += processed
            if not loop or self._should_stop:
                break
            logger.debug("Cycle completed; sleeping for %s seconds.", self.config.poll_interval)
            try:
                time.sleep(self.config.poll_interval)
            except KeyboardInterrupt:  # pragma: no cover - fallback
                logger.info("Interrupted; stopping.")
                break
        logger.info("Auto responder run finished. %s replies sent.", total_replies)

    def _process_inbox(self) -> int:
        replies_sent = 0
        imap = self._connect_imap()
        if imap is None:
            return replies_sent

        try:
            imap.select(self.config.mailbox)
            status, data = imap.uid("search", None, "UNSEEN")
            if status != "OK":
                logger.error("Failed to search mailbox: %s", status)
                return replies_sent
            uids = data[0].split()
            logger.info("Found %d unread message(s).", len(uids))
            for uid in uids:
                uid_str = uid.decode()
                if self.config.max_replies_per_run and replies_sent >= self.config.max_replies_per_run:
                    logger.info("Reached max replies per run (%s).", self.config.max_replies_per_run)
                    break
                if self.processed_store.contains(uid_str):
                    logger.debug("Message UID %s already processed; skipping.", uid_str)
                    continue
                status, msg_data = imap.uid("fetch", uid, "(RFC822)")
                if status != "OK":
                    logger.error("Failed to fetch message UID %s", uid_str)
                    continue
                raw_email = msg_data[0][1]
                message = email.message_from_bytes(raw_email)
                subject, body = extract_text_from_email(message)
                match = self.responder.match(subject, body)
                if match is None:
                    logger.debug("No matching rule for message UID %s.", uid_str)
                    continue
                response_template, rule, keyword = match
                if self._send_reply(message, response_template, rule, keyword):
                    replies_sent += 1
                    self.processed_store.add(uid_str)
                    imap.uid("store", uid, "+FLAGS", "(\\Seen \\Answered)")
        finally:
            try:
                imap.logout()
            except Exception:  # pragma: no cover - best effort
                logger.debug("Failed to log out from IMAP.", exc_info=True)
        return replies_sent

    def _connect_imap(self) -> Optional[imaplib.IMAP4]:
        try:
            if self.config.imap_use_ssl:
                imap = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
            else:
                imap = imaplib.IMAP4(self.config.imap_host, self.config.imap_port)
            imap.login(self.config.username, self.config.password)
            return imap
        except imaplib.IMAP4.error:
            logger.exception("IMAP authentication failed.")
        except Exception:
            logger.exception("Failed to connect to IMAP server.")
        return None

    def _send_reply(
        self,
        original_message: email.message.Message,
        template: ResponseTemplate,
        rule: Optional[KeywordRule],
        matched_keyword: str,
    ) -> bool:
        sender_name, sender_email = parseaddr(original_message.get("From", ""))
        if not sender_email:
            logger.warning("Original message missing sender; skipping auto reply.")
            return False

        to_addresses = [sender_email]
        if template.reply_to_all:
            cc = email.utils.getaddresses(original_message.get_all("Cc", []))
            cc_emails = [addr for _, addr in cc if addr and addr != self.config.username]
            to_addresses.extend(cc_emails)

        subject = decode_mime_words(original_message.get("Subject", ""))
        context = {
            "original_subject": subject,
            "original_sender": sender_email,
            "original_sender_name": sender_name,
            "matched_keyword": matched_keyword,
            "rule_name": rule.name if rule else "",
        }
        reply_subject = format_template(template.subject, context)
        reply_body = format_template(template.body, context)

        if template.include_original_message:
            original_text = "\n".join(
                [
                    "",
                    "----- 原始邮件 -----",
                    f"发件人: {sender_name} <{sender_email}>",
                    f"主题: {subject}",
                    "",
                    extract_text_from_email(original_message)[1],
                ]
            )
            reply_body = f"{reply_body.rstrip()}\n{original_text}"

        message = EmailMessage()
        message["Subject"] = reply_subject
        from_name = self.config.sender_name or ""
        message["From"] = formataddr((from_name, self.config.username)) if from_name else self.config.username
        message["To"] = ", ".join(sorted(set(to_addresses)))
        message["In-Reply-To"] = original_message.get("Message-ID", make_msgid())
        references = original_message.get_all("References", [])
        if references:
            references.append(original_message.get("Message-ID", ""))
            message["References"] = " ".join(filter(None, references))
        message.set_content(reply_body)

        try:
            if self.config.smtp_use_ssl:
                context_ssl = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port, context=context_ssl) as smtp:
                    smtp.login(self.config.username, self.config.password)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as smtp:
                    if self.config.smtp_use_starttls:
                        smtp.starttls(context=ssl.create_default_context())
                    smtp.login(self.config.username, self.config.password)
                    smtp.send_message(message)
            logger.info("Sent auto-reply to %s (rule: %s).", sender_email, rule.name if rule else "default")
            return True
        except smtplib.SMTPException:
            logger.exception("Failed to send reply to %s.", sender_email)
        return False


def format_template(template: str, context: Dict[str, str]) -> str:
    class SafeDict(dict):
        def __missing__(self, key):
            return ""

    return template.format_map(SafeDict(context))


def build_config_from_dict(config_dict: Dict) -> AutoResponderConfig:
    keyword_rules = []
    for rule_dict in config_dict.get("keyword_rules", []):
        response_dict = rule_dict.get("response", {})
        response = ResponseTemplate(
            subject=response_dict.get("subject", "Re: {original_subject}"),
            body=response_dict.get("body", ""),
            reply_to_all=response_dict.get("reply_to_all", False),
            include_original_message=response_dict.get("include_original_message", False),
        )
        keyword_rules.append(
            KeywordRule(
                name=rule_dict.get("name", "unnamed"),
                keywords=rule_dict.get("keywords", []),
                response=response,
                match_all=rule_dict.get("match_all", False),
                case_sensitive=rule_dict.get("case_sensitive", False),
                stop_processing=rule_dict.get("stop_processing", True),
            )
        )

    default_response_dict = config_dict.get("default_response")
    default_response = None
    if default_response_dict:
        default_response = ResponseTemplate(
            subject=default_response_dict.get("subject", "Re: {original_subject}"),
            body=default_response_dict.get("body", ""),
            reply_to_all=default_response_dict.get("reply_to_all", False),
            include_original_message=default_response_dict.get("include_original_message", False),
        )

    processed_store_path = Path(config_dict.get("processed_store", ".auto_responder_processed.json"))

    return AutoResponderConfig(
        imap_host=config_dict["imap"]["host"],
        imap_port=config_dict["imap"].get("port", 993),
        imap_use_ssl=config_dict["imap"].get("use_ssl", True),
        smtp_host=config_dict["smtp"]["host"],
        smtp_port=config_dict["smtp"].get("port", 465),
        smtp_use_ssl=config_dict["smtp"].get("use_ssl", True),
        smtp_use_starttls=config_dict["smtp"].get("use_starttls", False),
        username=config_dict["credentials"]["username"],
        sender_name=config_dict["credentials"].get("sender_name"),
        password=config_dict["credentials"]["password"],
        mailbox=config_dict.get("mailbox", "INBOX"),
        keyword_rules=keyword_rules,
        default_response=default_response,
        poll_interval=config_dict.get("poll_interval", 60),
        processed_store=processed_store_path,
        max_replies_per_run=config_dict.get("max_replies_per_run"),
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto reply to emails based on keyword matches.")
    parser.add_argument(
        "--config",
        "-c",
        default="email_auto_responder_config.json",
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Keep running and polling the inbox at the configured interval.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process the inbox only once. Overrides --loop.",
    )
    parser.add_argument(
        "--max-replies",
        type=int,
        help="Maximum number of replies to send during this run.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    configure_logging(args.log_level)

    config_path = Path(args.config)
    if not config_path.exists():
        logger.error("Configuration file %s does not exist.", config_path)
        return 1

    raw_config = load_json_config(config_path)
    config = build_config_from_dict(raw_config)

    if args.max_replies is not None:
        config.max_replies_per_run = args.max_replies

    responder = EmailAutoResponder(config)
    loop = args.loop and not args.once
    responder.run(loop=loop)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
