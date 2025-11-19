#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据Excel中的OSS图片URL批量删除对象的脚本。

核心能力：
1. 读取Excel文件中指定列的图片URL
2. 解析URL中的OSS桶名与对象路径
3. 利用配置文件中的AccessKey信息批量删除对象

使用示例：
    python oss_delete_from_excel.py \
        --excel input.xlsx \
        --column url \
        --config oss_monitor_config.json \
        --dry-run

依赖库：
    - pandas (读取Excel)
    - openpyxl (pandas读取xlsx所需)
    - oss2 (阿里云OSS SDK)
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse, unquote

try:
    import pandas as pd
except ImportError as exc:
    raise ImportError("未找到 pandas 库，请先执行 pip install pandas openpyxl") from exc

try:
    import oss2
except ImportError as exc:
    raise ImportError("未找到 oss2 库，请先执行 pip install oss2") from exc


@dataclass
class DeleteResult:
    url: str
    bucket: Optional[str]
    object_key: Optional[str]
    success: bool
    message: str


class OSSDeletionManager:
    """
    根据配置构造OSS Bucket客户端，并执行批量删除。
    """

    def __init__(self, config_path: str, dry_run: bool = False):
        self.config = self._load_config(config_path)
        self.dry_run = dry_run
        self.bucket_clients: Dict[str, oss2.Bucket] = {}
        self.domain_map: Dict[str, Dict[str, str]] = {}
        self._init_clients()
        self._init_domain_map()

    def _load_config(self, path: str) -> Dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"未找到配置文件: {path}")
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def _init_clients(self):
        buckets: List[Dict] = self.config.get("buckets", [])
        if not buckets:
            raise ValueError("配置文件中未找到 buckets 信息")

        for bucket_cfg in buckets:
            name = bucket_cfg.get("name")
            endpoint = bucket_cfg.get("endpoint")
            key_id = bucket_cfg.get("access_key_id")
            key_secret = bucket_cfg.get("access_key_secret")
            if not all([name, endpoint, key_id, key_secret]):
                logging.warning("跳过配置不完整的桶: %s", bucket_cfg)
                continue

            auth = oss2.Auth(key_id, key_secret)
            self.bucket_clients[name] = oss2.Bucket(auth, endpoint, name)
            logging.debug("已初始化桶客户端: %s (%s)", name, endpoint)

        if not self.bucket_clients:
            raise RuntimeError("未能初始化任何OSS桶客户端，请检查配置文件")

    def _init_domain_map(self):
        """
        支持配置文件中的自定义域名映射：
        {
            "custom_domains": [
                {"domain": "img.example.com", "bucket": "my-bucket", "endpoint": "https://oss-cn-hangzhou.aliyuncs.com"}
            ]
        }
        """
        mappings: List[Dict] = self.config.get("custom_domains", [])
        for item in mappings:
            domain = item.get("domain")
            bucket = item.get("bucket")
            endpoint = item.get("endpoint")
            if domain and bucket:
                self.domain_map[domain.lower()] = {
                    "bucket": bucket,
                    "endpoint": endpoint,
                }

    def delete_urls(self, urls: Iterable[str]) -> List[DeleteResult]:
        results: List[DeleteResult] = []
        for raw_url in urls:
            url = (raw_url or "").strip()
            if not url:
                continue

            try:
                bucket_name, object_key = self._parse_oss_location(url)
            except ValueError as err:
                results.append(
                    DeleteResult(
                        url=url,
                        bucket=None,
                        object_key=None,
                        success=False,
                        message=str(err),
                    )
                )
                continue

            bucket = self.bucket_clients.get(bucket_name)
            if bucket is None:
                results.append(
                    DeleteResult(
                        url=url,
                        bucket=bucket_name,
                        object_key=object_key,
                        success=False,
                        message=f"桶 {bucket_name} 未在配置文件中定义",
                    )
                )
                continue

            if self.dry_run:
                logging.info("[Dry Run] 将删除: bucket=%s, key=%s", bucket_name, object_key)
                results.append(
                    DeleteResult(
                        url=url,
                        bucket=bucket_name,
                        object_key=object_key,
                        success=True,
                        message="Dry run - 未实际删除",
                    )
                )
                continue

            try:
                bucket.delete_object(object_key)
                logging.info("删除成功: bucket=%s, key=%s", bucket_name, object_key)
                results.append(
                    DeleteResult(
                        url=url,
                        bucket=bucket_name,
                        object_key=object_key,
                        success=True,
                        message="删除成功",
                    )
                )
            except oss2.exceptions.NoSuchKey:
                msg = "对象不存在"
                logging.warning("%s: bucket=%s, key=%s", msg, bucket_name, object_key)
                results.append(
                    DeleteResult(
                        url=url,
                        bucket=bucket_name,
                        object_key=object_key,
                        success=False,
                        message=msg,
                    )
                )
            except Exception as err:  # pylint: disable=broad-except
                msg = f"删除失败: {err}"
                logging.error("%s - url=%s", msg, url)
                results.append(
                    DeleteResult(
                        url=url,
                        bucket=bucket_name,
                        object_key=object_key,
                        success=False,
                        message=msg,
                    )
                )

        return results

    def _parse_oss_location(self, url: str) -> Tuple[str, str]:
        """
        解析OSS URL，返回(bucket_name, object_key)。
        支持以下URL：
            - https://bucket-name.oss-cn-hangzhou.aliyuncs.com/path/to/file.jpg
            - https://oss-cn-hangzhou.aliyuncs.com/bucket-name/path/to/file.jpg
            - 自定义域名（需在custom_domains中配置）
        """
        parsed = urlparse(url)
        host = parsed.hostname or ""
        path = parsed.path.lstrip("/")

        if not host or not path:
            raise ValueError("URL缺少host或path，无法解析")

        host = host.lower()
        path = unquote(path)

        # 自定义域名映射
        if host in self.domain_map:
            mapping = self.domain_map[host]
            bucket_name = mapping["bucket"]
            if mapping.get("endpoint"):
                # 如果映射中包含endpoint但配置中没有相应bucket，则动态创建
                if bucket_name not in self.bucket_clients:
                    endpoint = mapping["endpoint"]
                    bucket_cfg = self._find_bucket_config(bucket_name, endpoint)
                    if bucket_cfg:
                        auth = oss2.Auth(bucket_cfg["access_key_id"], bucket_cfg["access_key_secret"])
                        self.bucket_clients[bucket_name] = oss2.Bucket(auth, endpoint, bucket_name)
                    else:
                        logging.warning("未在配置文件中找到桶 %s 的凭证，无法用于自定义域名 %s", bucket_name, host)
            return bucket_name, path

        # 子域名样式：bucket-name.oss-cn-region.aliyuncs.com
        if ".oss-" in host and host.endswith(".aliyuncs.com"):
            bucket_name = host.split(".oss-")[0]
            object_key = path
            return bucket_name, object_key

        # 路径样式：oss-cn-region.aliyuncs.com/bucket-name/object
        if host.startswith("oss-") and host.endswith(".aliyuncs.com"):
            parts = path.split("/", 1)
            if len(parts) != 2:
                raise ValueError("路径样式URL必须包含桶名和对象路径")
            bucket_name, object_key = parts
            return bucket_name, object_key

        raise ValueError("无法识别的OSS URL格式，请确认是否为标准OSS域名或配置了custom_domains")

    def _find_bucket_config(self, bucket_name: str, endpoint: str) -> Optional[Dict]:
        """尝试在配置文件中找到匹配桶的凭证。"""
        for bucket_cfg in self.config.get("buckets", []):
            if bucket_cfg.get("name") == bucket_name:
                if endpoint and bucket_cfg.get("endpoint") != endpoint:
                    continue
                return bucket_cfg
        return None


def load_urls_from_excel(excel_path: str, column_name: str, deduplicate: bool = True) -> List[str]:
    if not os.path.isfile(excel_path):
        raise FileNotFoundError(f"未找到Excel文件: {excel_path}")

    df = pd.read_excel(excel_path, engine="openpyxl")
    if column_name not in df.columns:
        raise KeyError(f"Excel中未找到列: {column_name}，可用列: {list(df.columns)}")

    urls = df[column_name].dropna().astype(str).tolist()
    if deduplicate:
        seen = set()
        deduped = []
        for url in urls:
            url = url.strip()
            if url and url not in seen:
                seen.add(url)
                deduped.append(url)
        return deduped
    return [url.strip() for url in urls if url.strip()]


def configure_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def summarize_results(results: List[DeleteResult]):
    total = len(results)
    success = sum(1 for r in results if r.success)
    failure = total - success
    logging.info("处理完成: 总计=%s, 成功=%s, 失败=%s", total, success, failure)

    if failure:
        logging.info("失败详情：")
        for item in results:
            if not item.success:
                logging.info(" - URL=%s | 桶=%s | 对象=%s | 原因=%s", item.url, item.bucket, item.object_key, item.message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="根据Excel中的OSS URL批量删除对象")
    parser.add_argument("--excel", required=True, help="包含URL的Excel文件路径")
    parser.add_argument("--column", default="url", help="Excel中存放URL的列名，默认:url")
    parser.add_argument("--config", default="oss_monitor_config.json", help="OSS凭证配置文件路径")
    parser.add_argument("--deduplicate", action="store_true", help="去重URL后再删除")
    parser.add_argument("--dry-run", action="store_true", help="仅打印将要删除的对象，不实际删除")
    parser.add_argument("--verbose", action="store_true", help="输出调试日志")
    return parser.parse_args()


def main():
    args = parse_args()
    configure_logging(args.verbose)

    logging.info("开始读取Excel: %s (列: %s)", args.excel, args.column)
    urls = load_urls_from_excel(args.excel, args.column, deduplicate=args.deduplicate)
    logging.info("共获取到 %s 条URL", len(urls))

    manager = OSSDeletionManager(config_path=args.config, dry_run=args.dry_run)
    results = manager.delete_urls(urls)
    summarize_results(results)


if __name__ == "__main__":
    main()
