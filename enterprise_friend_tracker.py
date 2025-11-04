#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业微信好友变更统计工具。

该脚本用于统计指定企业微信账号在指定日期范围内的新增客户数以及
被客户主动删除（或产生负反馈）的人数，并将结果保存到本地 JSON 文件。

用法示例：

    python enterprise_friend_tracker.py collect --config friend_tracker_config.json --date 2025-11-03
    python enterprise_friend_tracker.py collect --config friend_tracker_config.json --start-date 2025-10-01 --end-date 2025-10-07
    python enterprise_friend_tracker.py summary --config friend_tracker_config.json --limit 14

配置文件示例请参考 `friend_tracker_config.example.json`。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import requests

try:  # Python 3.9+
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - 针对旧版本 Python 的兼容处理
    try:
        from backports.zoneinfo import ZoneInfo  # type: ignore
    except ImportError as exc:  # pragma: no cover - 在项目环境中应提供依赖
        raise RuntimeError(
            "缺少 zoneinfo 模块。请在 Python 3.9+ 环境运行，或安装 backports.zoneinfo"
        ) from exc


LOGGER = logging.getLogger(__name__)


# WeCom 接口错误码，当 token 失效或需要刷新时会返回这些值
_TOKEN_EXPIRED_ERRCODES = {40014, 42001, 42007, 40082, 42009, 40001}


def _chunked(sequence: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    """按固定大小切片 sequence。"""

    if size <= 0:
        raise ValueError("chunk size must be positive")

    for idx in range(0, len(sequence), size):
        yield sequence[idx : idx + size]


def _first_present(data: Dict[str, Any], keys: Sequence[str], default: int = 0) -> int:
    """返回 data 中第一个存在且为数字的键值。"""

    for key in keys:
        if key in data and data[key] is not None:
            try:
                return int(data[key])
            except (ValueError, TypeError):
                LOGGER.debug("字段 %s=%r 无法转换为 int，忽略", key, data[key])
    return default


def _ensure_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class FriendStatRecord:
    """单个员工在某日的好友变更统计。"""

    date: str
    user_id: str
    new_contacts: int
    deleted_by_user: int
    stat_time: int
    retrieved_at: str
    raw_metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FriendStatRecord":
        return cls(
            date=data.get("date", ""),
            user_id=data.get("user_id", ""),
            new_contacts=_ensure_int(data.get("new_contacts")),
            deleted_by_user=_ensure_int(data.get("deleted_by_user")),
            stat_time=_ensure_int(data.get("stat_time")),
            retrieved_at=data.get("retrieved_at", ""),
            raw_metrics=data.get("raw_metrics", {}),
        )


class JSONStorage:
    """简单的 JSON 文件存储。"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._records: Dict[str, Dict[str, Any]] = {}
        self._load()

    @staticmethod
    def _key(date_str: str, user_id: str) -> str:
        return f"{date_str}::{user_id}"

    def _load(self) -> None:
        if not self.file_path.exists():
            self._records = {}
            return

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"无法解析存储文件 {self.file_path}: {exc}") from exc

        if not isinstance(data, list):
            raise RuntimeError(f"存储文件 {self.file_path} 格式错误，预期为列表")

        for item in data:
            if not isinstance(item, dict):
                continue
            key = self._key(item.get("date", ""), item.get("user_id", ""))
            self._records[key] = item

    def upsert(self, record: FriendStatRecord) -> None:
        key = self._key(record.date, record.user_id)
        self._records[key] = record.to_dict()

    def upsert_many(self, records: Iterable[FriendStatRecord]) -> None:
        for record in records:
            self.upsert(record)

    def save(self) -> None:
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

        sorted_items = sorted(
            self._records.values(), key=lambda item: (item.get("date", ""), item.get("user_id", ""))
        )

        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(sorted_items, f, ensure_ascii=False, indent=2)

    def list_records(self) -> List[FriendStatRecord]:
        return [FriendStatRecord.from_dict(item) for item in self._records.values()]


class WeComAPIError(RuntimeError):
    """企业微信接口错误。"""

    def __init__(self, message: str, errcode: int, payload: Dict[str, Any]):
        super().__init__(f"WeCom API error {errcode}: {message}")
        self.errcode = errcode
        self.payload = payload


class WeComClient:
    """企业微信 API 客户端。"""

    def __init__(
        self,
        corp_id: str,
        corp_secret: str,
        base_url: str = "https://qyapi.weixin.qq.com",
        timeout: float = 10.0,
        retries: int = 1,
    ) -> None:
        if not corp_id or not corp_secret:
            raise ValueError("corp_id 和 corp_secret 不能为空")

        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = max(0, retries)
        self._access_token: Optional[str] = None
        self._token_expire_at: Optional[datetime] = None

    def _ensure_access_token(self) -> None:
        if self._access_token and self._token_expire_at and datetime.utcnow() < self._token_expire_at:
            return

        url = f"{self.base_url}/cgi-bin/gettoken"
        resp = requests.get(
            url,
            params={"corpid": self.corp_id, "corpsecret": self.corp_secret},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        payload = resp.json()

        if payload.get("errcode", 0) != 0:
            raise WeComAPIError(payload.get("errmsg", "unknown"), payload.get("errcode", -1), payload)

        self._access_token = payload["access_token"]
        expires_in = _ensure_int(payload.get("expires_in"), 7200)
        # 提前 120 秒刷新，避免边界问题
        self._token_expire_at = datetime.utcnow() + timedelta(seconds=max(60, expires_in - 120))
        LOGGER.debug("获取 access_token 成功，将在 %s 过期", self._token_expire_at)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._ensure_access_token()

        url = f"{self.base_url}{path}"
        attempt = 0

        while True:
            attempt += 1
            query = dict(params or {})
            query["access_token"] = self._access_token

            response = requests.request(
                method,
                url,
                params=query,
                json=json_data,
                timeout=self.timeout,
            )

            response.raise_for_status()
            payload = response.json()

            errcode = payload.get("errcode", 0)

            if errcode == 0:
                return payload

            if errcode in _TOKEN_EXPIRED_ERRCODES and attempt <= self.retries + 1:
                LOGGER.debug("token 可能过期，尝试刷新后重试 (attempt=%s)", attempt)
                self._access_token = None
                self._ensure_access_token()
                continue

            raise WeComAPIError(payload.get("errmsg", "unknown"), errcode, payload)

    def get_user_behavior_data(
        self,
        user_ids: Sequence[str],
        party_ids: Sequence[int],
        start_time: int,
        end_time: int,
    ) -> List[Dict[str, Any]]:
        """调用获取「联系客户」统计数据接口。"""

        all_behavior: List[Dict[str, Any]] = []
        user_ids = tuple(user_ids)
        party_ids = tuple(party_ids)

        if not user_ids and not party_ids:
            raise ValueError("配置中必须至少提供 user_ids 或 party_ids 之一")

        # 接口限制一次最多 100 个员工
        userid_chunks = list(_chunked(user_ids, 100)) or [()]

        for chunk in userid_chunks:
            payload = {
                "userid_list": list(chunk),
                "partyid_list": list(party_ids),
                "start_time": start_time,
                "end_time": end_time,
            }

            # 如果 chunk 为空，接口要求至少传递一个字段，因此仅在第一轮且有 partyid 时允许
            if not chunk and party_ids:
                payload.pop("userid_list", None)

            result = self.request(
                "POST",
                "/cgi-bin/externalcontact/get_user_behavior_data",
                json_data=payload,
            )

            behavior_data = result.get("behavior_data", [])
            if isinstance(behavior_data, list):
                all_behavior.extend(behavior_data)

        return all_behavior


class WeComFriendTracker:
    """企业微信好友变更统计主类。"""

    NEW_CONTACT_KEYS = (
        "new_contact_cnt",
        "new_customer_cnt",
        "new_external_contact_cnt",
    )

    DELETE_CONTACT_KEYS = (
        "customer_contact_del_cnt",
        "customer_contact_delete_cnt",
        "delete_customer_cnt",
        "lose_customer_cnt",
        "negative_feedback_cnt",
    )

    def __init__(self, config: Dict[str, Any]) -> None:
        request_cfg = config.get("request", {})
        self.timezone = ZoneInfo(config.get("timezone", "Asia/Shanghai"))
        self.user_ids: Tuple[str, ...] = tuple(config.get("user_ids", []) or [])
        self.party_ids: Tuple[int, ...] = tuple(config.get("party_ids", []) or [])

        self.client = WeComClient(
            corp_id=config["corp_id"],
            corp_secret=config["corp_secret"],
            base_url=request_cfg.get("base_url", "https://qyapi.weixin.qq.com"),
            timeout=request_cfg.get("timeout", 10.0),
            retries=request_cfg.get("retries", 1),
        )

        storage_path = config.get("storage", {}).get("file_path", "data/friend_stats.json")
        self.storage = JSONStorage(storage_path)

    def _date_span(self, target_date: date) -> Tuple[int, int]:
        start_dt = datetime.combine(target_date, time.min, tzinfo=self.timezone)
        end_dt = datetime.combine(target_date, time.max, tzinfo=self.timezone)
        return int(start_dt.timestamp()), int(end_dt.timestamp())

    def _normalise_record(
        self,
        entry: Dict[str, Any],
        default_date: date,
        default_stat_time: int,
    ) -> FriendStatRecord:
        stat_ts = _ensure_int(entry.get("stat_time"), default_stat_time)

        try:
            stat_date = datetime.fromtimestamp(stat_ts, tz=self.timezone).date()
        except (OverflowError, OSError, ValueError):
            stat_date = default_date

        user_id = entry.get("userid") or entry.get("user_id") or "unknown"

        new_contacts = _first_present(entry, self.NEW_CONTACT_KEYS, default=0)
        deleted_by_user = _first_present(entry, self.DELETE_CONTACT_KEYS, default=0)

        raw_metrics = dict(entry)

        record = FriendStatRecord(
            date=stat_date.isoformat(),
            user_id=str(user_id),
            new_contacts=new_contacts,
            deleted_by_user=deleted_by_user,
            stat_time=stat_ts,
            retrieved_at=datetime.now(self.timezone).isoformat(timespec="seconds"),
            raw_metrics=raw_metrics,
        )
        return record

    def collect_for_date(self, target_date: date) -> List[FriendStatRecord]:
        start_ts, end_ts = self._date_span(target_date)

        behavior_data = self.client.get_user_behavior_data(
            user_ids=self.user_ids,
            party_ids=self.party_ids,
            start_time=start_ts,
            end_time=end_ts,
        )

        records: List[FriendStatRecord] = []

        for entry in behavior_data:
            record = self._normalise_record(entry, target_date, start_ts)
            # 过滤到请求日期
            if record.date == target_date.isoformat():
                records.append(record)

        # 如果某些 userid 没有返回数据，为其补零记录
        present_users = {rec.user_id for rec in records}
        for uid in self.user_ids:
            if uid not in present_users:
                records.append(
                    FriendStatRecord(
                        date=target_date.isoformat(),
                        user_id=uid,
                        new_contacts=0,
                        deleted_by_user=0,
                        stat_time=start_ts,
                        retrieved_at=datetime.now(self.timezone).isoformat(timespec="seconds"),
                        raw_metrics={"note": "API 未返回该用户的数据，默认记为 0"},
                    )
                )

        self.storage.upsert_many(records)
        self.storage.save()

        return records

    def collect_range(self, start_date: date, end_date: date) -> List[FriendStatRecord]:
        if end_date < start_date:
            raise ValueError("end_date 不能早于 start_date")

        current = start_date
        all_records: List[FriendStatRecord] = []

        while current <= end_date:
            LOGGER.info("正在采集 %s 的好友统计数据", current.isoformat())
            daily_records = self.collect_for_date(current)
            if daily_records:
                new_total = sum(r.new_contacts for r in daily_records)
                del_total = sum(r.deleted_by_user for r in daily_records)
                LOGGER.info(
                    "  -> 新增好友 %s 人，被客户删除 %s 人", new_total, del_total
                )
            else:
                LOGGER.info("  -> 当日无数据返回")
            all_records.extend(daily_records)
            current += timedelta(days=1)

        return all_records

    def summarise(self, records: Iterable[FriendStatRecord], aggregate: bool = True) -> List[Tuple[str, int, int]]:
        summary: Dict[str, Dict[str, int]] = {}

        for record in records:
            summary.setdefault(record.date, {"new": 0, "deleted": 0})
            summary[record.date]["new"] += record.new_contacts
            summary[record.date]["deleted"] += record.deleted_by_user

        ordered = sorted(summary.items(), key=lambda item: item[0])

        if aggregate:
            return [(date_str, values["new"], values["deleted"]) for date_str, values in ordered]

        # 若不聚合，则直接展开
        detailed: List[Tuple[str, int, int]] = []
        for record in records:
            detailed.append((f"{record.date}::{record.user_id}", record.new_contacts, record.deleted_by_user))
        return sorted(detailed, key=lambda item: item[0])

    def print_summary(self, records: Iterable[FriendStatRecord], aggregate: bool = True) -> None:
        entries = list(self.summarise(records, aggregate=aggregate))
        if not entries:
            LOGGER.info("暂无可展示的数据")
            return

        header = "日期" if aggregate else "日期/用户"
        LOGGER.info("%s | 新增好友 | 被客户删除", header)
        LOGGER.info("%s", "-" * 40)
        for label, new_cnt, del_cnt in entries:
            LOGGER.info("%s | %4d | %4d", label, new_cnt, del_cnt)


def load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件 {path} 不存在")

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config, dict):
        raise ValueError("配置文件格式错误，应为 JSON 对象")

    return config


def setup_logging(config: Dict[str, Any]) -> None:
    logging_cfg = config.get("logging", {})
    level_name = logging_cfg.get("level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    log_file = logging_cfg.get("file")
    if log_file:
        log_path = Path(log_file)
        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=handlers,
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="企业微信好友变更统计工具")
    parser.add_argument("--config", default="friend_tracker_config.json", help="配置文件路径")

    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="采集指定日期范围内的数据")
    collect_parser.add_argument("--date", help="目标日期 (YYYY-MM-DD)")
    collect_parser.add_argument("--start-date", help="开始日期 (YYYY-MM-DD)")
    collect_parser.add_argument("--end-date", help="结束日期 (YYYY-MM-DD)")
    collect_parser.add_argument("--days", type=int, help="向前追溯的天数（与 end-date 搭配使用）")
    collect_parser.add_argument(
        "--print-summary", action="store_true", help="采集完成后打印汇总表"
    )

    summary_parser = subparsers.add_parser("summary", help="打印已有数据的汇总表")
    summary_parser.add_argument("--limit", type=int, default=30, help="展示最近 N 天的数据")
    summary_parser.add_argument(
        "--detailed", action="store_true", help="展示按用户拆分的明细"
    )

    return parser.parse_args(argv)


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"无法解析日期 {value}, 期望格式 YYYY-MM-DD") from exc


def determine_date_range(args: argparse.Namespace) -> Tuple[date, date]:
    if args.date:
        target = parse_date(args.date)
        return target, target

    start_date: Optional[date] = parse_date(args.start_date) if args.start_date else None
    end_date: Optional[date] = parse_date(args.end_date) if args.end_date else None

    if start_date and end_date:
        return start_date, end_date

    if end_date and args.days:
        start_date = end_date - timedelta(days=max(0, args.days - 1))
        return start_date, end_date

    if start_date and args.days:
        end_date = start_date + timedelta(days=max(0, args.days - 1))
        return start_date, end_date

    # 默认采集昨天的数据
    default_date = datetime.now().date() - timedelta(days=1)
    return default_date, default_date


def cmd_collect(args: argparse.Namespace, tracker: WeComFriendTracker) -> None:
    start_date, end_date = determine_date_range(args)
    records = tracker.collect_range(start_date, end_date)
    if args.print_summary:
        tracker.print_summary(records, aggregate=True)


def cmd_summary(args: argparse.Namespace, tracker: WeComFriendTracker) -> None:
    records = tracker.storage.list_records()
    if not records:
        LOGGER.info("存储中暂无数据，请先执行 collect 命令。")
        return

    records.sort(key=lambda r: (r.date, r.user_id))

    if args.limit:
        cutoff = datetime.now().date() - timedelta(days=max(args.limit - 1, 0))
        records = [r for r in records if parse_date(r.date) >= cutoff]

    tracker.print_summary(records, aggregate=not args.detailed)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    config = load_config(args.config)
    setup_logging(config)

    tracker = WeComFriendTracker(config)

    if args.command == "collect":
        cmd_collect(args, tracker)
    elif args.command == "summary":
        cmd_summary(args, tracker)
    else:  # pragma: no cover - 理论上不会执行
        raise ValueError(f"未知命令: {args.command}")


if __name__ == "__main__":
    try:
        main()
    except WeComAPIError as exc:
        LOGGER.error("调用企业微信接口失败: %s", exc)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - 捕获顶层异常并输出
        LOGGER.exception("程序运行失败: %s", exc)
        sys.exit(1)
