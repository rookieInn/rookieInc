#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常用户检测与日报发送器
- 基于 tracking_analytics.detect_abusive_users
- 每日生成报告并发送到管理员邮箱（可选）
"""

from __future__ import annotations

import sys
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List
from datetime import datetime
from configparser import ConfigParser

from tracking_models import TrackingDatabase
from tracking_analytics import TrackingAnalytics


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file: str = 'config.ini') -> ConfigParser:
    cfg = ConfigParser()
    cfg.read(config_file, encoding='utf-8')
    return cfg


def build_thresholds(cfg: ConfigParser) -> Dict[str, Any]:
    sec = 'abuse_detection'
    return {
        'per_minute_threshold': cfg.getint(sec, 'per_minute_threshold', fallback=120),
        'daily_event_threshold': cfg.getint(sec, 'daily_event_threshold', fallback=5000),
        'form_submit_threshold': cfg.getint(sec, 'form_submit_threshold', fallback=300),
        'identical_event_ratio_threshold': cfg.getfloat(sec, 'identical_event_ratio_threshold', fallback=0.9),
    }


def format_report(result: Dict[str, Any]) -> Dict[str, str]:
    period = result.get('period', {})
    stats = result.get('stats', {})
    abusers: List[Dict[str, Any]] = result.get('abusers', [])

    title = f"异常用户日报 - {datetime.now().strftime('%Y-%m-%d')}"

    # 文本版
    lines = []
    lines.append(title)
    lines.append('=' * len(title))
    lines.append(f"时间范围: {period.get('start_date')} ~ {period.get('end_date')}")
    lines.append(f"事件总数: {stats.get('total_events', 0)}  唯一用户: {stats.get('unique_users', 0)}  唯一IP: {stats.get('unique_ips', 0)}")
    lines.append("")

    if not abusers:
        lines.append("未发现疑似异常用户 ✅")
    else:
        lines.append(f"发现疑似异常主体 {len(abusers)} 个：")
        for i, a in enumerate(abusers, 1):
            entity = a.get('user_id') or a.get('ip_address') or 'unknown'
            tag = 'user_id' if 'user_id' in a else 'ip'
            lines.append(
                f"{i}. [{tag}] {entity} | 峰值/分钟: {a['peak_per_minute']} | 单日: {a['daily_events']} | "
                f"form_submit: {a['form_submits']} | 同质占比: {a['identical_event_ratio']:.2f} | 规则: {','.join(a['triggers'])}"
            )
            if a.get('top_signature'):
                lines.append(f"   top_signature: {a['top_signature']}")
    text_report = "\n".join(lines)

    # HTML版
    html_lines = [
        f"<h2>{title}</h2>",
        f"<p>时间范围: {period.get('start_date')} ~ {period.get('end_date')}</p>",
        f"<p>事件总数: <b>{stats.get('total_events', 0)}</b> &nbsp; 唯一用户: <b>{stats.get('unique_users', 0)}</b> &nbsp; 唯一IP: <b>{stats.get('unique_ips', 0)}</b></p>",
    ]
    if not abusers:
        html_lines.append("<p>未发现疑似异常用户 ✅</p>")
    else:
        html_lines.append(f"<p>发现疑似异常主体 <b>{len(abusers)}</b> 个：</p>")
        html_lines.append("<table border='1' cellspacing='0' cellpadding='6'>")
        html_lines.append("<tr><th>#</th><th>主体</th><th>类型</th><th>峰值/分钟</th><th>单日</th><th>form_submit</th><th>同质占比</th><th>触发规则</th><th>top_signature</th></tr>")
        for i, a in enumerate(abusers, 1):
            entity = a.get('user_id') or a.get('ip_address') or 'unknown'
            tag = 'user_id' if 'user_id' in a else 'ip'
            html_lines.append(
                "<tr>"
                f"<td>{i}</td><td>{entity}</td><td>{tag}</td>"
                f"<td>{a['peak_per_minute']}</td><td>{a['daily_events']}</td><td>{a['form_submits']}</td>"
                f"<td>{a['identical_event_ratio']:.2f}</td><td>{', '.join(a['triggers'])}</td>"
                f"<td>{a.get('top_signature','')}</td>"
                "</tr>"
            )
        html_lines.append("</table>")
    html_report = "\n".join(html_lines)

    return {"text": text_report, "html": html_report, "subject": title}


def send_email(cfg: ConfigParser, subject: str, text_body: str, html_body: str) -> None:
    email_sec = 'email'
    enabled = cfg.getboolean(email_sec, 'enabled', fallback=False)
    if not enabled:
        logger.info("邮件发送未启用（email.enabled = false），仅输出到控制台")
        print(text_body)
        return

    smtp_host = cfg.get(email_sec, 'smtp_host', fallback='')
    smtp_port = cfg.getint(email_sec, 'smtp_port', fallback=587)
    use_tls = cfg.getboolean(email_sec, 'use_tls', fallback=True)
    username = cfg.get(email_sec, 'username', fallback='')
    password = cfg.get(email_sec, 'password', fallback='')
    from_addr = cfg.get(email_sec, 'from_addr', fallback='')
    to_addrs_raw = cfg.get(email_sec, 'to_addrs', fallback='')

    if not (smtp_host and from_addr and to_addrs_raw):
        raise ValueError('邮件配置不完整（smtp_host/from_addr/to_addrs）')

    to_addrs = [a.strip() for a in to_addrs_raw.split(',') if a.strip()]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ", ".join(to_addrs)

    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    server = None
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password)
        server.sendmail(from_addr, to_addrs, msg.as_string())
        logger.info("📧 异常用户报告已发送")
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass


def run(days: int = 1) -> int:
    cfg = load_config()

    # 阈值
    th = build_thresholds(cfg)

    # 数据库和分析
    db = TrackingDatabase()
    analytics = TrackingAnalytics(db)

    result = analytics.detect_abusive_users(
        days=days,
        per_minute_threshold=th['per_minute_threshold'],
        daily_event_threshold=th['daily_event_threshold'],
        form_submit_threshold=th['form_submit_threshold'],
        identical_event_ratio_threshold=th['identical_event_ratio_threshold'],
    )

    report = format_report(result)
    try:
        send_email(cfg, report['subject'], report['text'], report['html'])
        return 0
    except Exception as e:
        logger.error(f"发送报告失败: {e}")
        print(report['text'])
        return 1
    finally:
        db.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='异常用户检测与日报发送器')
    parser.add_argument('--days', type=int, default=1, help='分析天数（默认1天）')
    args = parser.parse_args()
    sys.exit(run(days=args.days))
