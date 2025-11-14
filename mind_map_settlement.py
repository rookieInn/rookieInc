#!/usr/bin/env python3
"""
Mind-map style settlement calculator with N-ary tree support.

Features
--------
- 支持树形结构的金额汇总、拆分、比例分配、定额分配以及自动按权重平分。
- 每个节点可以定义抵扣项（单个数值或详细列表）。
- 自动生成文本报表，并可选择导出计算结果 JSON。
- 可选生成类似思维导图的可视化（依赖 matplotlib，可选安装）。

使用示例
--------
1. 写入示例配置：
   python mind_map_settlement.py --write-template settlement_example.json

2. 运行并输出报表、图片：
   python mind_map_settlement.py --config settlement_example.json --save-figure settlement.png
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


EPSILON = 1e-6


def _fmt_currency(value: float) -> str:
    return f"¥{value:,.2f}"


def _ensure_positive(value: float, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as err:
        raise ValueError(f"{label} 需要是数字, 当前值: {value!r}") from err
    if number < -EPSILON:
        raise ValueError(f"{label} 不允许为负数, 当前值: {number}")
    return number


def _parse_ratio(value: Any) -> float:
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        number = float(cleaned)
        if "%" in value:
            number /= 100.0
        elif number > 1:
            # 如果用户直接写了 30 表示 30%
            number /= 100.0
    else:
        number = float(value)
    if number < -EPSILON:
        raise ValueError(f"比例不能为负数: {value}")
    return number


def _normalize_deductions(entry: Any) -> Tuple[float, List[Dict[str, Any]]]:
    if entry is None:
        return 0.0, []
    if isinstance(entry, (int, float)):
        return float(entry), []
    if isinstance(entry, dict):
        if "amount" not in entry:
            raise ValueError("抵扣对象需要包含 amount 字段")
        amount = _ensure_positive(entry["amount"], "抵扣金额")
        label = entry.get("label", "未命名")
        return amount, [{"label": label, "amount": amount}]
    if isinstance(entry, list):
        total = 0.0
        details: List[Dict[str, Any]] = []
        for item in entry:
            if not isinstance(item, dict) or "amount" not in item:
                raise ValueError("抵扣项需要形如 {'label': '税费', 'amount': 2000}")
            amount = _ensure_positive(item["amount"], "抵扣金额")
            total += amount
            details.append({"label": item.get("label", "未命名"), "amount": amount})
        return total, details
    raise ValueError("deductions 仅支持数字/字典/列表形式")


@dataclass
class SettlementNodeResult:
    name: str
    amount: float
    net_amount: float
    deductions: float
    deduction_details: List[Dict[str, Any]]
    allocation_note: str
    retained: float
    note: Optional[str]
    metadata: Dict[str, Any]
    children: List["SettlementNodeResult"] = field(default_factory=list)

    @property
    def distributed(self) -> float:
        return sum(child.amount for child in self.children)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "amount": self.amount,
            "deductions": self.deductions,
            "net_amount": self.net_amount,
            "retained": self.retained,
            "allocation_note": self.allocation_note,
            "note": self.note,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children],
        }


def compute_settlement_tree(
    config: Dict[str, Any],
    *,
    parent_amount: Optional[float] = None,
    depth: int = 0,
    forced_amount: Optional[float] = None,
    allocation_hint: Optional[str] = None,
) -> SettlementNodeResult:
    name = config.get("name", f"未命名节点@{depth}")
    note = config.get("note")
    metadata = config.get("metadata", {})

    amount, allocation_note = _resolve_base_amount(
        config,
        parent_amount=parent_amount,
        forced_amount=forced_amount,
        allocation_hint=allocation_hint,
    )

    deductions_value, deduction_details = _normalize_deductions(config.get("deductions"))
    if deductions_value - amount > EPSILON:
        raise ValueError(f"{name} 的抵扣金额({deductions_value})大于可用金额({amount})")
    net_amount = amount - deductions_value

    children_cfg = config.get("children", []) or []
    children_results: List[SettlementNodeResult] = []
    if children_cfg:
        children_results = _compute_children(
            children_cfg,
            parent_net=net_amount,
            depth=depth + 1,
        )

    distributed = sum(child.amount for child in children_results)
    if distributed - net_amount > EPSILON:
        raise ValueError(
            f"{name} 子节点分配金额({distributed})超过可分配净额({net_amount})，"
            "请检查比例/定额设定。"
        )
    retained = max(net_amount - distributed, 0.0)

    return SettlementNodeResult(
        name=name,
        amount=amount,
        net_amount=net_amount,
        deductions=deductions_value,
        deduction_details=deduction_details,
        allocation_note=allocation_note,
        retained=retained,
        note=note,
        metadata=metadata,
        children=children_results,
    )


def _resolve_base_amount(
    config: Dict[str, Any],
    *,
    parent_amount: Optional[float],
    forced_amount: Optional[float],
    allocation_hint: Optional[str],
) -> Tuple[float, str]:
    if forced_amount is not None:
        amount = forced_amount
        note = allocation_hint or f"按上级自动分配 {_fmt_currency(amount)}"
        return amount, note

    if "amount" in config:
        amount = _ensure_positive(config["amount"], f"{config.get('name','节点')} 金额")
        return amount, "固定金额"

    allocation = config.get("allocation")
    if allocation:
        alloc_type = allocation.get("type", "ratio")
        if alloc_type == "ratio":
            if parent_amount is None:
                raise ValueError("比例分配需要上级金额")
            ratio = _parse_ratio(allocation.get("value", 0))
            amount = parent_amount * ratio
            note = allocation.get("label") or f"占上级 {ratio * 100:.2f}%"
            return amount, note
        if alloc_type == "fixed":
            amount = _ensure_positive(allocation.get("value", 0), "定额分配")
            note = allocation.get("label") or "上级定额"
            return amount, note
        raise ValueError(f"不支持的 allocation.type: {alloc_type}")

    if parent_amount is None:
        raise ValueError("根节点必须指定 amount")

    return parent_amount, "继承上级"


def _compute_children(
    children_cfg: List[Dict[str, Any]],
    *,
    parent_net: float,
    depth: int,
) -> List[SettlementNodeResult]:
    ratio_total = 0.0
    fixed_consumed = 0.0
    weight_candidates: List[Dict[str, Any]] = []

    for child in children_cfg:
        if "amount" in child:
            fixed_consumed += _ensure_positive(child["amount"], f"{child.get('name','子节点')} 金额")
            continue
        allocation = child.get("allocation")
        if allocation:
            alloc_type = allocation.get("type", "ratio")
            if alloc_type == "ratio":
                ratio_total += _parse_ratio(allocation.get("value", 0))
            elif alloc_type == "fixed":
                fixed_consumed += _ensure_positive(allocation.get("value", 0), "定额分配")
            else:
                raise ValueError(f"不支持的 allocation.type: {alloc_type}")
        else:
            weight_candidates.append(child)

    if ratio_total - 1.0 > EPSILON:
        raise ValueError(f"同级节点的比例总和超过 100% (当前 {ratio_total * 100:.2f}%)")

    ratio_amount = ratio_total * parent_net
    if fixed_consumed - parent_net > EPSILON:
        raise ValueError("定额/固定金额之和超过上级可分配净额")
    remaining = parent_net - fixed_consumed - ratio_amount
    if remaining < -EPSILON:
        raise ValueError("比例+定额之和超过上级可分配净额")
    remaining = max(remaining, 0.0)

    total_weight = sum(child.get("weight", 1) for child in weight_candidates) or 0

    results: List[SettlementNodeResult] = []
    for child in children_cfg:
        allocation_hint = None
        forced_amount: Optional[float] = None
        if child in weight_candidates:
            weight = child.get("weight", 1)
            if total_weight == 0:
                forced_amount = 0.0
                allocation_hint = "无剩余可分配"
            else:
                share = weight / total_weight
                forced_amount = remaining * share
                allocation_hint = f"按权重 {weight}/{total_weight} (≈{share * 100:.2f}%)"
        elif "amount" in child:
            forced_amount = _ensure_positive(child["amount"], f"{child.get('name','子节点')} 金额")
            allocation_hint = "直接指定金额"
        elif child.get("allocation", {}).get("type") == "fixed":
            # 为保持显示一致性，提前生成提示
            forced_amount = None
            value = _ensure_positive(child["allocation"]["value"], "定额分配")
            allocation_hint = child["allocation"].get("label") or f"上级定额 {_fmt_currency(value)}"

        child_result = compute_settlement_tree(
            child,
            parent_amount=parent_net,
            depth=depth,
            forced_amount=forced_amount,
            allocation_hint=allocation_hint,
        )
        results.append(child_result)

    return results


def render_table(root: SettlementNodeResult) -> str:
    rows: List[Tuple[str, float, float, float, float, str]] = []

    def _walk(node: SettlementNodeResult, prefix: List[str]) -> None:
        path = " > ".join(prefix + [node.name])
        rows.append(
            (
                path,
                node.amount,
                node.deductions,
                node.net_amount,
                node.retained,
                node.allocation_note,
            )
        )
        for child in node.children:
            _walk(child, prefix + [node.name])

    _walk(root, [])
    headers = ("节点路径", "分配金额", "抵扣", "净额", "留存", "分配说明")
    col_widths = [len(h) for h in headers]

    for idx, row in enumerate(rows):
        formatted = [
            row[0],
            _fmt_currency(row[1]),
            _fmt_currency(row[2]),
            _fmt_currency(row[3]),
            _fmt_currency(row[4]),
            row[5],
        ]
        rows[idx] = tuple(formatted)  # type: ignore
        for col_idx, value in enumerate(formatted):
            col_widths[col_idx] = max(col_widths[col_idx], len(value))

    def _format_line(values: Tuple[str, ...]) -> str:
        return " | ".join(value.ljust(col_widths[idx]) for idx, value in enumerate(values))

    output = [_format_line(headers), "-+-".join("-" * w for w in col_widths)]
    for row in rows:
        output.append(_format_line(row))
    return "\n".join(output)


def export_result_json(root: SettlementNodeResult, path: Path) -> None:
    path.write_text(json.dumps(root.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已导出计算结果至 {path}")


def plot_tree(root: SettlementNodeResult, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("未安装 matplotlib，跳过可视化生成。可通过 pip install matplotlib 安装。")
        return

    nodes, edges = _flatten_nodes(root)
    leaf_counts = _leaf_count_map(root)
    positions = _assign_positions(root, leaf_counts, nodes)

    fig, ax = plt.subplots(figsize=(12, 6))
    for parent_idx, child_idx in edges:
        x_values = [positions[parent_idx][0], positions[child_idx][0]]
        y_values = [positions[parent_idx][1], positions[child_idx][1]]
        ax.plot(x_values, y_values, color="#888888", linewidth=1.2, zorder=1)

    for node_info in nodes:
        idx = node_info["idx"]
        node = node_info["node"]
        x, y = positions[idx]
        ax.scatter([x], [y], color="#1f77b4", s=80, zorder=2)
        label_lines = [
            node.name,
            f"金额: {_fmt_currency(node.amount)}",
            f"净额: {_fmt_currency(node.net_amount)}",
        ]
        if node.deductions > EPSILON:
            label_lines.append(f"抵扣: {_fmt_currency(node.deductions)}")
        if node.retained > EPSILON:
            label_lines.append(f"留存: {_fmt_currency(node.retained)}")
        ax.text(
            x,
            y,
            "\n".join(label_lines),
            ha="center",
            va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f6f6f6", edgecolor="#555555"),
            zorder=3,
        )

    ax.set_axis_off()
    ax.set_title("思维导图式结算视图", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    print(f"可视化已保存至 {output_path}")


def _flatten_nodes(root: SettlementNodeResult) -> Tuple[List[Dict[str, Any]], List[Tuple[int, int]]]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Tuple[int, int]] = []

    def _walk(node: SettlementNodeResult, parent_idx: Optional[int] = None) -> None:
        idx = len(nodes)
        nodes.append({"idx": idx, "node": node})
        if parent_idx is not None:
            edges.append((parent_idx, idx))
        for child in node.children:
            _walk(child, idx)

    _walk(root)
    return nodes, edges


def _leaf_count_map(root: SettlementNodeResult) -> Dict[int, int]:
    cache: Dict[int, int] = {}

    def _count(node: SettlementNodeResult) -> int:
        node_id = id(node)
        if node_id in cache:
            return cache[node_id]
        if not node.children:
            cache[node_id] = 1
        else:
            cache[node_id] = sum(_count(child) for child in node.children)
        return cache[node_id]

    _count(root)
    return cache


def _assign_positions(
    root: SettlementNodeResult,
    leaf_counts: Dict[int, int],
    nodes_info: List[Dict[str, Any]],
) -> Dict[int, Tuple[float, float]]:
    positions: Dict[int, Tuple[float, float]] = {}
    node_id_to_index = {id(info["node"]): info["idx"] for info in nodes_info}
    total_leaves = leaf_counts[id(root)]

    def _place(node: SettlementNodeResult, depth: int, x_start: float, x_end: float) -> None:
        idx = node_id_to_index[id(node)]
        x = (x_start + x_end) / 2.0
        y = -depth
        positions[idx] = (x, y)
        cursor = x_start
        for child in node.children:
            span = (leaf_counts[id(child)] / total_leaves) * (x_end - x_start)
            _place(child, depth + 1, cursor, cursor + span)
            cursor += span

    _place(root, depth=0, x_start=0.0, x_end=1.0)
    return positions


DEFAULT_EXAMPLE = {
    "name": "项目总收入",
    "amount": 280000,
    "deductions": [
        {"label": "税费", "amount": 25000},
        {"label": "平台手续费", "amount": 5000},
    ],
    "children": [
        {
            "name": "渠道伙伴",
            "allocation": {"type": "ratio", "value": "35%"},
            "children": [
                {
                    "name": "渠道A",
                    "allocation": {"type": "ratio", "value": 0.6},
                },
                {
                    "name": "渠道B",
                    "allocation": {"type": "ratio", "value": 0.4},
                    "deductions": {"label": "返点调整", "amount": 2000},
                },
            ],
        },
        {
            "name": "运营执行团队",
            "allocation": {"type": "ratio", "value": "25%"},
            "children": [
                {"name": "技术支持", "weight": 2},
                {"name": "活动执行", "weight": 3},
            ],
        },
        {
            "name": "固定成本",
            "allocation": {"type": "fixed", "value": 40000, "label": "固定成本 4 万"},
            "children": [
                {"name": "场地", "amount": 15000},
                {"name": "设备折旧", "amount": 25000},
            ],
        },
        {
            "name": "公司留存",
            "weight": 1,
            "children": [
                {"name": "备用金", "allocation": {"type": "ratio", "value": 0.5}},
                {"name": "分红池", "allocation": {"type": "ratio", "value": 0.5}},
            ],
        },
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="思维导图式结算/分摊计算器",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="输入 JSON 配置文件路径。若不提供则使用内置示例。",
    )
    parser.add_argument(
        "--write-template",
        type=Path,
        help="将示例配置写入指定路径并退出（若同时指定 --config 则继续运行）。",
    )
    parser.add_argument(
        "--save-figure",
        type=Path,
        help="若提供路径，则生成 PNG 思维导图图像。",
    )
    parser.add_argument(
        "--export-json",
        type=Path,
        help="导出计算结果为 JSON。",
    )
    parser.add_argument(
        "--no-table",
        action="store_true",
        help="不在终端输出文本报表。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.write_template:
        args.write_template.write_text(
            json.dumps(DEFAULT_EXAMPLE, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"示例配置已写入 {args.write_template}")
        if not args.config:
            return

    if args.config:
        if not args.config.exists():
            raise FileNotFoundError(f"配置文件不存在: {args.config}")
        config_data = json.loads(args.config.read_text(encoding="utf-8"))
    else:
        config_data = DEFAULT_EXAMPLE
        print("未提供配置文件，使用内置示例。")

    root = compute_settlement_tree(config_data)

    if not args.no_table:
        print(render_table(root))

    if args.export_json:
        export_result_json(root, args.export_json)

    if args.save_figure:
        plot_tree(root, args.save_figure)


if __name__ == "__main__":
    main()
