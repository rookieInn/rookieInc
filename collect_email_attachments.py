#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect attachments from emails in an IMAP mailbox within a given time range.

Examples
--------
Download attachments from the last 7 days to ./attachments:

    python collect_email_attachments.py \
        --imap-server imap.example.com \
        --username alice@example.com \
        --ask-password \
        --output-dir ./attachments

Download attachments between two dates:

    python collect_email_attachments.py \
        --imap-server imap.example.com \
        --username alice@example.com \
        --password-env-var MAIL_PASSWORD \
        --since 2025-01-01 \
        --until 2025-01-31 \
        --output-dir ./january_attachments
"""

from __future__ import annotations

import argparse
import getpass
import imaplib
import logging
import mimetypes
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from email import message_from_bytes, policy
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable, List, Optional


# --------------------------------------------------------------------------- #
# Data structures and helpers
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class DateRange:
    """Inclusive date range used for filtering emails."""

    since: Optional[date]
    until: Optional[date]

    @property
    def before_date(self) -> Optional[date]:
        """Translate the inclusive end date to the IMAP BEFORE date (exclusive)."""
        if self.until is None:
            return None
        return self.until + timedelta(days=1)


def parse_iso_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"无效日期格式: {value!r}，需使用 YYYY-MM-DD") from exc


def ensure_positive(value: int, option: str) -> None:
    if value <= 0:
        raise argparse.ArgumentTypeError(f"{option} 必须为正整数")


def imap_fmt(value: date) -> str:
    """Convert a Python date to the IMAP expected format."""
    return value.strftime("%d-%b-%Y")


def decode_mime_words(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def sanitize_filename(raw: str) -> str:
    """Strip path separators, control characters, and trim length."""
    sanitized = "".join(
        "_" if ch in '<>:"/\\|?*' or ord(ch) < 32 else ch for ch in raw
    ).strip(" .")
    if not sanitized:
        sanitized = "attachment"
    return sanitized[:200]


def ensure_unique_path(path: Path) -> Path:
    """Ensure the resulting path is unique by appending a numeric suffix."""
    if not path.exists():
        return path
    counter = 1
    stem = path.stem
    suffix = path.suffix
    while True:
        candidate = path.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def resolve_password(args: argparse.Namespace) -> str:
    if args.password:
        return args.password
    if args.password_env_var:
        env_value = os.environ.get(args.password_env_var)
        if env_value:
            return env_value
        raise SystemExit(
            f"环境变量 {args.password_env_var} 未设置，无法获取密码"
        )
    if args.ask_password:
        return getpass.getpass("IMAP 密码: ")
    raise SystemExit("请通过 --password、--password-env-var 或 --ask-password 提供 IMAP 密码")


def resolve_date_range(args: argparse.Namespace) -> DateRange:
    today = datetime.now().date()

    until = parse_iso_date(args.until) if args.until else None
    since = parse_iso_date(args.since) if args.since else None
    days = args.days

    if since and days is not None:
        raise SystemExit("不能同时使用 --since 和 --days 选项")

    if days is None and not since and not until:
        days = 7  # 默认最近 7 天

    if days is not None:
        ensure_positive(days, "--days")
        reference_until = until or today
        since = reference_until - timedelta(days=days - 1)
        until = reference_until

    if until is None:
        until = today

    if since and since > until:
        raise SystemExit(f"起始日期 {since} 晚于结束日期 {until}")

    return DateRange(since=since, until=until)


def configure_logging(level: str) -> None:
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise SystemExit(f"未知日志级别: {level}")
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def iter_message_attachments(message: EmailMessage) -> Iterable[EmailMessage]:
    if hasattr(message, "iter_attachments"):
        yield from message.iter_attachments()
        return
    for part in message.walk():
        if part.is_multipart():
            continue
        content_disposition = part.get("Content-Disposition", "")
        if "attachment" in content_disposition.lower():
            yield part


# --------------------------------------------------------------------------- #
# Core collection logic
# --------------------------------------------------------------------------- #

def collect_attachments(args: argparse.Namespace) -> None:
    password = resolve_password(args)
    configure_logging(args.log_level)

    date_range = resolve_date_range(args)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.info("连接 IMAP 服务器 %s:%s", args.imap_server, args.imap_port)
    try:
        client = imaplib.IMAP4_SSL(args.imap_server, args.imap_port)
        client.login(args.username, password)
    except imaplib.IMAP4.error as exc:
        raise SystemExit(f"IMAP 登录失败: {exc}") from exc

    with client:
        status, _ = client.select(args.mailbox)
        if status != "OK":
            raise SystemExit(f"无法选择邮箱 {args.mailbox!r}: {status}")

        search_terms: List[str] = ["ALL"]
        if date_range.since:
            search_terms.extend(["SINCE", imap_fmt(date_range.since)])
        if date_range.before_date:
            search_terms.extend(["BEFORE", imap_fmt(date_range.before_date)])

        logging.info(
            "搜索条件: %s (邮箱: %s)",
            " ".join(search_terms),
            args.mailbox,
        )

        status, data = client.search(None, *search_terms)
        if status != "OK":
            raise SystemExit(f"搜索邮件失败: {status}")

        raw_ids = data[0]
        if not raw_ids:
            logging.info("未找到匹配的邮件")
            return

        message_ids = [msg_id.decode("utf-8") for msg_id in raw_ids.split()]
        message_ids.sort(key=int)

        if args.max_emails:
            ensure_positive(args.max_emails, "--max-emails")
            message_ids = message_ids[-args.max_emails :]

        logging.info("共找到 %d 封符合条件的邮件", len(message_ids))

        total_messages = 0
        attachments_saved = 0
        attachments_skipped = 0

        for msg_id in message_ids:
            status, msg_data = client.fetch(msg_id, "(RFC822)")
            if status != "OK":
                logging.warning("获取邮件 %s 失败，跳过", msg_id)
                continue

            message_bytes = next(
                (part[1] for part in msg_data if isinstance(part, tuple)),
                None,
            )
            if message_bytes is None:
                logging.warning("邮件 %s 没有可解析内容，跳过", msg_id)
                continue

            message = message_from_bytes(message_bytes, policy=policy.default)
            subject = decode_mime_words(message.get("Subject", ""))
            sender = decode_mime_words(message.get("From", ""))
            sent_at = None
            if "Date" in message:
                try:
                    sent_at = parsedate_to_datetime(message["Date"])
                except (TypeError, ValueError):
                    sent_at = None

            total_messages += 1
            logging.debug(
                "处理邮件 #%s: 来自 %s | 主题 %s | 日期 %s",
                msg_id,
                sender or "(未知)",
                subject or "(无主题)",
                sent_at.isoformat() if sent_at else "(未知)",
            )

            attachment_found = False
            for index, part in enumerate(iter_message_attachments(message), start=1):
                attachment_found = True
                filename = part.get_filename()
                if filename:
                    filename = decode_mime_words(filename)
                else:
                    guessed_ext = mimetypes.guess_extension(part.get_content_type() or "")
                    filename = f"attachment_{msg_id}_{index}{guessed_ext or '.bin'}"

                filename = sanitize_filename(filename)
                target_path = output_dir / filename

                if target_path.exists():
                    if args.skip_existing:
                        logging.info("附件已存在，跳过: %s", target_path.name)
                        attachments_skipped += 1
                        continue
                    target_path = ensure_unique_path(target_path)

                if args.dry_run:
                    logging.info("DRY-RUN: 将保存附件 %s -> %s", filename, target_path.name)
                    attachments_saved += 1
                    continue

                payload = part.get_payload(decode=True)
                if payload is None:
                    logging.warning("附件 %s 无有效内容，跳过", filename)
                    attachments_skipped += 1
                    continue

                with target_path.open("wb") as file_obj:
                    file_obj.write(payload)

                attachments_saved += 1
                logging.info(
                    "保存附件: %s | 邮件: %s | 发件人: %s",
                    target_path.name,
                    subject or "(无主题)",
                    sender or "(未知)",
                )

            if not attachment_found:
                logging.debug("邮件 #%s 无附件", msg_id)

        logging.info("处理完成: %d 封邮件, 保存附件 %d 个, 跳过 %d 个", total_messages, attachments_saved, attachments_skipped)


# --------------------------------------------------------------------------- #
# CLI entrypoint
# --------------------------------------------------------------------------- #

def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="将指定时间范围内邮件的附件下载到本地文件夹",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--imap-server", required=True, help="IMAP 服务器地址")
    parser.add_argument("--imap-port", type=int, default=993, help="IMAP 服务器端口")
    parser.add_argument("--username", required=True, help="邮箱账号")

    password_group = parser.add_mutually_exclusive_group()
    password_group.add_argument("--password", help="邮箱密码（直接提供，不推荐）")
    password_group.add_argument("--password-env-var", help="包含邮箱密码的环境变量名称")
    password_group.add_argument("--ask-password", action="store_true", help="交互式输入密码")

    parser.add_argument("--mailbox", default="INBOX", help="IMAP 邮箱文件夹名称")
    parser.add_argument("--output-dir", required=True, help="附件保存目录")
    parser.add_argument("--since", help="起始日期（含，当提供 --days 时不可用），格式 YYYY-MM-DD")
    parser.add_argument("--until", help="结束日期（含），格式 YYYY-MM-DD，默认今天")
    parser.add_argument("--days", type=int, help="向前追溯的天数（默认最近 7 天）")
    parser.add_argument("--max-emails", type=int, help="最多处理的邮件数量，按时间倒序")
    parser.add_argument("--skip-existing", action="store_true", help="若附件已存在同名文件则跳过")
    parser.add_argument("--dry-run", action="store_true", help="仅打印计划执行的操作，不实际下载")
    parser.add_argument("--log-level", default="INFO", help="日志级别")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        collect_attachments(args)
    except KeyboardInterrupt:
        logging.warning("用户中断")
        return 130
    except Exception as exc:
        logging.error(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

