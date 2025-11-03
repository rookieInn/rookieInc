"""Command line interface for the order processing pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from .config import PipelineConfig, load_config
from .pipeline import OrderProcessingPipeline, PipelineResult


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="清洗电商订单数据并输出异常订单报告",
    )
    parser.add_argument("--raw", required=True, help="原始订单 CSV/Parquet 文件路径")
    parser.add_argument("--historical", help="用于补全物流单号的历史订单文件")
    parser.add_argument("--clean-output", required=True, help="清洗后数据输出 CSV 路径")
    parser.add_argument("--anomaly-output", required=True, help="异常订单报告输出 CSV 路径")
    parser.add_argument("--config", help="自定义 JSON 配置文件路径")
    parser.add_argument(
        "--disable-ml",
        action="store_true",
        help="关闭基于 Isolation Forest 的 AI 异常检测",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="在控制台打印处理摘要",
    )
    parser.add_argument(
        "--summary-path",
        help="将处理摘要输出为 JSON 文件",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    config = load_config(args.config) if args.config else PipelineConfig()
    if args.disable_ml:
        config.anomaly.isolation_forest.enabled = False

    pipeline = OrderProcessingPipeline(config)
    result = pipeline.run_to_files(
        raw_orders_path=args.raw,
        cleaned_output_path=args.clean_output,
        anomaly_report_path=args.anomaly_output,
        historical_orders_path=args.historical,
    )

    summary = build_summary(result)

    if args.summary:
        print(format_summary(summary))

    if args.summary_path:
        path = Path(args.summary_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=2)

    return 0


def build_summary(result: PipelineResult) -> Dict[str, Any]:
    anomalies = result.anomalies
    anomaly_counts: Dict[str, int] = {}
    if not anomalies.empty:
        anomaly_counts = anomalies["anomaly_type"].value_counts().to_dict()

    summary = {
        "cleaning_stats": result.cleaning_stats,
        "anomaly_total": int(len(anomalies)),
        "anomaly_breakdown": anomaly_counts,
    }

    if result.tracking_imputations is not None and not result.tracking_imputations.empty:
        summary["tracking_imputations"] = len(result.tracking_imputations)

    return summary


def format_summary(summary: Dict[str, Any]) -> str:
    parts = ["=== 订单处理摘要 ==="]
    cleaning_stats = summary.get("cleaning_stats", {})
    if cleaning_stats:
        parts.append("数据清洗:")
        for key, value in cleaning_stats.items():
            parts.append(f"  - {key}: {value}")

    parts.append(f"异常订单总数: {summary.get('anomaly_total', 0)}")
    breakdown = summary.get("anomaly_breakdown", {})
    if breakdown:
        parts.append("异常类型分布:")
        for anomaly_type, count in breakdown.items():
            parts.append(f"  - {anomaly_type}: {count}")

    if "tracking_imputations" in summary:
        parts.append(f"补全物流单号数量: {summary['tracking_imputations']}")

    return "\n".join(parts)


if __name__ == "__main__":
    raise SystemExit(main())

