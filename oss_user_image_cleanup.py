#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云OSS用户图片清理脚本
======================

结合数据库记录清理OSS中多余的图片资源：对每位用户的每个模型仅保留指定数量（默认10）最新的图片，
其余的会被删除（支持干运行预览模式）。

使用示例：
    python3 oss_user_image_cleanup.py --config oss_cleanup_config.json --dry-run
    python3 oss_user_image_cleanup.py --config oss_cleanup_config.json --execute --yes
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

try:
    import oss2
except ImportError:  # pragma: no cover - dependency hint
    print("请安装oss2库: pip install oss2")
    sys.exit(1)

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:  # pragma: no cover - dependency hint
    print("请安装PyMySQL库: pip install PyMySQL")
    sys.exit(1)


def chunked(seq: Sequence[Any], size: int) -> Iterable[List[Any]]:
    """Yield successive chunks from seq."""
    for i in range(0, len(seq), size):
        yield list(seq[i : i + size])


@dataclass
class ImageRecord:
    """简单的数据行结构，用于辅助排序和日志输出。"""

    row_id: Any
    user_id: Any
    model_name: str
    oss_key: str
    sort_value: Any
    created_at: Optional[datetime]

    def short_repr(self) -> str:
        timestamp = (
            self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(self.created_at, datetime)
            else str(self.created_at)
        )
        return f"id={self.row_id}, user={self.user_id}, model={self.model_name}, key={self.oss_key}, created_at={timestamp}"


class DatabaseManager:
    """封装数据库交互逻辑。"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn: Optional[pymysql.connections.Connection] = None

    def __enter__(self) -> "DatabaseManager":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        if self.conn:
            return
        self.conn = pymysql.connect(
            host=self.config.get("host", "127.0.0.1"),
            port=int(self.config.get("port", 3306)),
            user=self.config.get("user"),
            password=self.config.get("password"),
            database=self.config.get("name"),
            charset=self.config.get("charset", "utf8mb4"),
            cursorclass=DictCursor,
            autocommit=False,
        )
        logging.info("✅ 已连接数据库 %s:%s/%s", self.config.get("host"), self.config.get("port"), self.config.get("name"))

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            finally:
                self.conn = None

    def fetch_image_rows(
        self,
        user_id: Optional[str] = None,
        model_name: Optional[str] = None,
        limit: Optional[int] = None,
        extra_only_models: Optional[Sequence[str]] = None,
        ignored_models: Optional[Sequence[str]] = None,
    ) -> List[ImageRecord]:
        """读取需要参与清理的图片记录。"""
        if not self.conn:
            raise RuntimeError("数据库尚未连接")

        table = self.config["table"]
        id_col = self.config.get("id_column", "id")
        user_col = self.config.get("user_column", "user_id")
        model_col = self.config.get("model_column", "model_name")
        oss_key_col = self.config.get("oss_key_column", "oss_key")
        created_col = self.config.get("created_at_column")
        sort_col = self.config.get("sort_column") or created_col or id_col
        sort_desc = self.config.get("sort_desc", True)

        select_fields = [
            f"{id_col} AS row_id",
            f"{user_col} AS user_id",
            f"{model_col} AS model_name" if model_col else f"NULL AS model_name",
            f"{oss_key_col} AS oss_key",
            f"{sort_col} AS sort_value",
        ]
        if created_col and created_col != sort_col:
            select_fields.append(f"{created_col} AS created_at")
        elif created_col:
            select_fields.append(f"{created_col} AS created_at")
        else:
            select_fields.append("NULL AS created_at")

        query = [f"SELECT {', '.join(select_fields)} FROM {table}"]
        where_clauses = ["1=1"]
        params: List[Any] = []

        # 附加过滤条件
        filters: Dict[str, Any] = self.config.get("extra_filters") or {}
        for column, value in filters.items():
            if isinstance(value, (list, tuple, set)):
                placeholders = ", ".join(["%s"] * len(value))
                where_clauses.append(f"{column} IN ({placeholders})")
                params.extend(list(value))
            else:
                where_clauses.append(f"{column} = %s")
                params.append(value)

        if user_id is not None:
            where_clauses.append(f"{user_col} = %s")
            params.append(user_id)
        if model_name is not None:
            where_clauses.append(f"{model_col} = %s")
            params.append(model_name)

        if extra_only_models:
            placeholders = ", ".join(["%s"] * len(extra_only_models))
            where_clauses.append(f"{model_col} IN ({placeholders})")
            params.extend(list(extra_only_models))

        if ignored_models:
            placeholders = ", ".join(["%s"] * len(ignored_models))
            where_clauses.append(f"{model_col} NOT IN ({placeholders})")
            params.extend(list(ignored_models))

        query.append("WHERE " + " AND ".join(where_clauses))
        order_dir = "DESC" if sort_desc else "ASC"
        query.append(f"ORDER BY {sort_col} {order_dir}")
        if limit is not None:
            query.append(f"LIMIT {int(limit)}")

        sql = "\n".join(query)
        logging.debug("执行SQL: %s | 参数: %s", sql, params)

        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        records: List[ImageRecord] = []
        for row in rows:
            model_value = row.get("model_name") or "__unknown__"
            created_raw = row.get("created_at")
            created_at = None
            if isinstance(created_raw, datetime):
                created_at = created_raw
            elif isinstance(created_raw, str):
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                    try:
                        created_at = datetime.strptime(created_raw.split(".")[0], fmt)
                        break
                    except ValueError:
                        continue
            records.append(
                ImageRecord(
                    row_id=row.get("row_id"),
                    user_id=row.get("user_id"),
                    model_name=str(model_value),
                    oss_key=row.get("oss_key"),
                    sort_value=row.get("sort_value"),
                    created_at=created_at,
                )
            )

        logging.info("📥 从数据库读取 %d 条图片记录", len(records))
        return records

    def delete_rows(self, row_ids: Sequence[Any], chunk_size: int = 500):
        """根据主键批量删除数据库记录。"""
        if not row_ids:
            return
        if not self.conn:
            raise RuntimeError("数据库尚未连接")

        id_col = self.config.get("id_column", "id")
        table = self.config["table"]
        deleted = 0

        try:
            with self.conn.cursor() as cursor:
                for chunk in chunked(list(row_ids), chunk_size):
                    placeholders = ", ".join(["%s"] * len(chunk))
                    sql = f"DELETE FROM {table} WHERE {id_col} IN ({placeholders})"
                    cursor.execute(sql, chunk)
                    deleted += cursor.rowcount
            self.conn.commit()
            logging.info("🗑️ 已删除数据库记录 %d 条", deleted)
        except Exception:
            self.conn.rollback()
            logging.exception("数据库删除失败，已回滚事务")
            raise


class OSSManager:
    """封装OSS对象删除逻辑。"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        auth = oss2.Auth(config["access_key_id"], config["access_key_secret"])
        self.bucket = oss2.Bucket(auth, config["endpoint"], config["bucket_name"])
        self.prefix = (config.get("object_prefix") or "").lstrip("/")
        logging.info("✅ 已连接OSS桶 %s", config["bucket_name"])

    def _normalize_key(self, key: Optional[str]) -> Optional[str]:
        if not key:
            return None
        key = key.strip()
        if not key:
            return None
        if key.lower().startswith("http"):
            parsed = urlparse(key)
            key = parsed.path.lstrip("/")
        else:
            key = key.lstrip("/")
        if self.prefix:
            prefix = self.prefix.rstrip("/") + "/"
            if key.startswith(prefix):
                return key
            return prefix + key
        return key

    def delete_objects(self, keys: Sequence[str], dry_run: bool = True, chunk_size: int = 500) -> Tuple[int, int]:
        """批量删除OSS对象，返回(成功数量, 失败数量)。"""
        normalized = []
        for key in keys:
            normalized_key = self._normalize_key(key)
            if normalized_key:
                normalized.append(normalized_key)

        if not normalized:
            return (0, 0)

        unique_keys = list(dict.fromkeys(normalized))  # 去重并保持顺序
        logging.info("准备删除 OSS 对象 %d 个（去重后）", len(unique_keys))

        if dry_run:
            logging.info("当前为干运行模式，OSS对象不会被实际删除")
            return (0, 0)

        deleted = 0
        failed = 0
        for chunk in chunked(unique_keys, chunk_size):
            try:
                result = self.bucket.batch_delete_objects(chunk, quiet=True)
                deleted += len(result.deleted_keys)
                failed += len(getattr(result, "delete_keys_error", []))
            except Exception:
                logging.exception("批量删除OSS对象失败: %s", chunk)
                failed += len(chunk)

        logging.info("OSS对象删除完成：成功 %d，失败 %d", deleted, failed)
        return deleted, failed


class CleanupManager:
    """主业务控制器。"""

    def __init__(self, config: Dict[str, Any], args: argparse.Namespace):
        self.config = config
        self.args = args
        self.cleanup_cfg = config.get("cleanup", {})

        # 日志
        log_cfg = config.get("logging", {})
        log_level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
        logging.basicConfig(
            level=getattr(logging, args.log_level.upper(), log_level) if args.log_level else log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_cfg.get("file", "oss_cleanup.log"), encoding="utf-8"),
            ],
        )

        # 运行模式
        if args.execute:
            self.dry_run = False
        elif args.dry_run:
            self.dry_run = True
        else:
            self.dry_run = bool(self.cleanup_cfg.get("dry_run", True))

        self.max_keep = args.max_keep or int(self.cleanup_cfg.get("max_images_per_model", 10))
        self.batch_size = int(self.cleanup_cfg.get("batch_size", 500))

        self.only_models = set(self.cleanup_cfg.get("only_models", []))
        self.only_models.update(args.only_model or [])

        self.ignored_models = set(self.cleanup_cfg.get("ignored_models", []))
        self.ignored_models.update(args.ignore_model or [])

        self.db = DatabaseManager(config["database"])
        self.oss = OSSManager(config["oss"])

    def run(self):
        logging.info("🚀 启动OSS用户图片清理（dry_run=%s, max_keep=%s）", self.dry_run, self.max_keep)
        with self.db:
            records = self.db.fetch_image_rows(
                user_id=self.args.user_id,
                model_name=self.args.model,
                limit=self.args.limit,
                extra_only_models=list(self.only_models) if self.only_models else None,
                ignored_models=list(self.ignored_models) if self.ignored_models else None,
            )

            to_delete, stats = self._select_deletions(records)
            if not to_delete:
                logging.info("🎉 没有需要删除的图片，任务结束")
                return

            self._log_summary(stats)

            if not self.dry_run and not self.args.yes:
                confirm = input("⚠️ 确认执行删除操作？输入 'yes' 继续：").strip().lower()
                if confirm not in {"y", "yes"}:
                    logging.info("用户取消操作")
                    return

            oss_keys = [record.oss_key for record in to_delete if record.oss_key]
            row_ids = [record.row_id for record in to_delete]

            logging.info("计划删除 OSS 对象 %d 个，数据库记录 %d 条", len(oss_keys), len(row_ids))

            oss_deleted, oss_failed = self.oss.delete_objects(oss_keys, dry_run=self.dry_run, chunk_size=self.batch_size)
            if not self.dry_run:
                self.db.delete_rows(row_ids, chunk_size=self.batch_size)

            logging.info(
                "✅ 清理完成 | OSS删除: %s 成功 / %s 失败 | DB删除: %s | 模式: %s",
                oss_deleted,
                oss_failed,
                0 if self.dry_run else len(row_ids),
                "干运行" if self.dry_run else "实际执行",
            )

    def _select_deletions(self, records: Sequence[ImageRecord]) -> Tuple[List[ImageRecord], Dict[Tuple[Any, str], Dict[str, int]]]:
        """根据配置筛选需要删除的记录。"""
        groups: Dict[Tuple[Any, str], List[ImageRecord]] = defaultdict(list)

        for record in records:
            model = record.model_name or "__unknown__"
            groups[(record.user_id, model)].append(record)

        summary: Dict[Tuple[Any, str], Dict[str, int]] = {}
        deletions: List[ImageRecord] = []

        for key, group in groups.items():
            group.sort(key=lambda r: (self._record_sort_value(r), r.row_id), reverse=True)
            total = len(group)
            if total <= self.max_keep:
                continue
            delete_count = total - self.max_keep
            deletions.extend(group[self.max_keep :])
            summary[key] = {
                "total": total,
                "delete": delete_count,
                "keep": self.max_keep,
            }

        logging.info("需要删除的图片总数：%d", len(deletions))
        return deletions, summary

    def _log_summary(self, stats: Dict[Tuple[Any, str], Dict[str, int]]):
        if not stats:
            return
        logging.info("🧾 清理概要（按用户/模型）：")
        for (user_id, model), data in sorted(stats.items(), key=lambda item: (str(item[0][0]), str(item[0][1]))):
            logging.info(
                " - 用户 %s | 模型 %s | 总计 %s | 保留 %s | 删除 %s",
                user_id,
                model,
                data.get("total"),
                data.get("keep"),
                data.get("delete"),
            )

    def _record_sort_value(self, record: ImageRecord) -> float:
        """将记录的排序字段转换为可比较的数字，便于统一排序。"""
        value = record.sort_value
        if isinstance(value, datetime):
            return value.timestamp()
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            base = value.split(".")[0]
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(base, fmt).timestamp()
                except ValueError:
                    continue
            try:
                return float(value)
            except ValueError:
                pass
        if record.created_at:
            return record.created_at.timestamp()
        if value is None:
            return float("-inf")
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("-inf")


def load_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="结合数据库、按用户/模型对OSS图片做留存清理")
    parser.add_argument("--config", default="oss_cleanup_config.json", help="配置文件路径")
    parser.add_argument("--user-id", help="仅处理指定用户")
    parser.add_argument("--model", help="仅处理指定模型")
    parser.add_argument("--only-model", action="append", help="仅处理这些模型，可多次指定")
    parser.add_argument("--ignore-model", action="append", help="跳过的模型，可多次指定")
    parser.add_argument("--limit", type=int, help="限制扫描的记录数量（调试用）")
    parser.add_argument("--max-keep", type=int, help="每个用户/模型保留的最大图片数")
    parser.add_argument("--dry-run", action="store_true", help="强制启用干运行（只预览）")
    parser.add_argument("--execute", action="store_true", help="执行实际删除，覆盖配置中的dry_run")
    parser.add_argument("--yes", action="store_true", help="无需确认直接执行删除")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="覆盖配置中的日志级别")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        config = load_config(args.config)
    except Exception as exc:
        print(f"❌ 读取配置失败: {exc}")
        sys.exit(1)

    try:
        manager = CleanupManager(config, args)
        manager.run()
    except KeyboardInterrupt:
        logging.warning("用户中断操作")
    except Exception as exc:  # pragma: no cover - CLI level safeguard
        logging.exception("清理流程失败: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
