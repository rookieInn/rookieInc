#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量将视频片段转换为 GIF。

该脚本依赖系统已安装 `ffmpeg`，可对单个文件或整个目录进行处理，
并通过两阶段（palettegen + paletteuse）流程获得更优的 GIF 质量。
"""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

DEFAULT_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm"}
DITHER_CHOICES = [
    "none",
    "bayer",
    "floyd_steinberg",
    "sierra2",
    "sierra2_4a",
    "sierra3",
    "burkes",
    "ed",
    "jarvis",
    "stucki",
    "atkinson",
]
PALETTE_STATS_MODES = ("full", "single")
SCALE_ALGOS = ("lanczos", "bicubic", "bilinear", "neighbor")


@dataclass(frozen=True)
class ClipSource:
    """记录待处理的源视频及其所属根目录。"""

    path: Path
    root: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将一个或多个视频片段批量转换为 GIF（基于 ffmpeg）"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="待处理的视频文件或目录（可同时提供多个）",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="gif_outputs",
        help="GIF 输出目录，默认：gif_outputs",
    )
    parser.add_argument(
        "--start",
        help="截取起始时间（例如 00:00:03 或 3.5），默认从头开始",
    )
    parser.add_argument(
        "--duration",
        help="截取时长（例如 2.5 或 00:00:05），默认处理到视频结束",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=12,
        help="输出 GIF 的帧率，默认 12",
    )
    parser.add_argument(
        "--width",
        type=int,
        help="目标宽度，默认保持原始宽度（与 --height 配合可缩放）",
    )
    parser.add_argument(
        "--height",
        type=int,
        help="目标高度，默认保持原始高度（与 --width 配合可缩放）",
    )
    parser.add_argument(
        "--scale-algorithm",
        choices=SCALE_ALGOS,
        default="lanczos",
        help="缩放算法，默认 lanczos",
    )
    parser.add_argument(
        "--max-colors",
        type=int,
        default=256,
        help="palette 最大颜色数，默认 256",
    )
    parser.add_argument(
        "--palette-mode",
        choices=PALETTE_STATS_MODES,
        default="full",
        help="palette 统计模式（full/single），默认 full",
    )
    parser.add_argument(
        "--dither",
        choices=DITHER_CHOICES,
        default="sierra2_4a",
        help="GIF 漫画抖动算法，默认 sierra2_4a",
    )
    parser.add_argument(
        "--loop",
        type=int,
        default=0,
        help="GIF 循环次数，0 表示无限循环，默认 0",
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="输出文件名追加的后缀，例如 `_clip`，默认不追加",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        help="自定义识别的视频扩展名（无需加点），默认支持常见格式",
    )
    parser.add_argument(
        "--preserve-structure",
        action="store_true",
        help="在输出目录中保留原始的子目录层级",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="若目标 GIF 已存在则覆盖，默认跳过",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅输出将要执行的操作，不真正调用 ffmpeg",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示 ffmpeg 命令及更多日志",
    )
    parser.add_argument(
        "--log-level",
        default="warning",
        choices=[
            "quiet",
            "panic",
            "fatal",
            "error",
            "warning",
            "info",
            "verbose",
            "debug",
            "trace",
        ],
        help="ffmpeg 日志级别，默认 warning",
    )
    return parser.parse_args()


def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        print("未检测到 ffmpeg，请先安装后再运行本工具。", file=sys.stderr)
        sys.exit(2)


def normalize_extensions(exts: Sequence[str] | None) -> set[str]:
    if not exts:
        return {ext.lower() for ext in DEFAULT_EXTENSIONS}
    normalized = set()
    for ext in exts:
        ext = ext.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.add(ext)
    return normalized or {ext.lower() for ext in DEFAULT_EXTENSIONS}


def collect_sources(
    inputs: Sequence[str], extensions: set[str]
) -> List[ClipSource]:
    sources: List[ClipSource] = []
    for raw_path in inputs:
        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            print(f"⚠️  跳过不存在的路径: {path}")
            continue
        if path.is_file():
            if path.suffix.lower() in extensions:
                sources.append(ClipSource(path=path, root=path.parent))
            else:
                print(f"⚠️  不支持的文件格式: {path.name}")
            continue
        # 目录
        for file in sorted(path.rglob("*")):
            if file.is_file() and file.suffix.lower() in extensions:
                sources.append(ClipSource(path=file.resolve(), root=path))
    return sources


def build_output_path(
    clip: ClipSource, output_dir: Path, preserve_structure: bool, suffix: str
) -> Path:
    if preserve_structure:
        try:
            relative_parent = clip.path.parent.relative_to(clip.root)
        except ValueError:
            relative_parent = Path()
        target_dir = output_dir / relative_parent
    else:
        target_dir = output_dir
    name = f"{clip.path.stem}{suffix}.gif"
    return target_dir / name


def build_base_filters(args: argparse.Namespace) -> str:
    filters: List[str] = []
    if args.fps and args.fps > 0:
        filters.append(f"fps={args.fps}")
    if args.width or args.height:
        width = args.width if args.width else -1
        height = args.height if args.height else -1
        filters.append(
            f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags={args.scale_algorithm}"
        )
    return ",".join(filters)


def build_palette_filter(base_filters: str, args: argparse.Namespace) -> str:
    palette = (
        f"palettegen=max_colors={args.max_colors}:stats_mode={args.palette_mode}"
    )
    if base_filters:
        return f"{base_filters},{palette}"
    return palette


def build_filter_complex(base_filters: str, args: argparse.Namespace) -> str:
    paletteuse = f"paletteuse=dither={args.dither}"
    if base_filters:
        return f"[0:v]{base_filters}[x];[x][1:v]{paletteuse}"
    return f"[0:v][1:v]{paletteuse}"


def run_command(cmd: Sequence[str], verbose: bool) -> None:
    if verbose:
        printable = " ".join(shlex.quote(part) for part in cmd)
        print(f"执行命令: {printable}")
    subprocess.run(cmd, check=True)


def build_palette_command(
    source: Path, palette_path: Path, palette_filter: str, args: argparse.Namespace
) -> List[str]:
    cmd = ["ffmpeg", "-hide_banner", "-y", "-loglevel", args.log_level]
    if args.start:
        cmd.extend(["-ss", str(args.start)])
    if args.duration:
        cmd.extend(["-t", str(args.duration)])
    cmd.extend(["-i", str(source), "-vf", palette_filter, str(palette_path)])
    return cmd


def build_gif_command(
    source: Path,
    palette_path: Path,
    output_path: Path,
    filter_complex: str,
    args: argparse.Namespace,
) -> List[str]:
    cmd = ["ffmpeg", "-hide_banner", "-y", "-loglevel", args.log_level]
    if args.start:
        cmd.extend(["-ss", str(args.start)])
    if args.duration:
        cmd.extend(["-t", str(args.duration)])
    cmd.extend(
        [
            "-i",
            str(source),
            "-i",
            str(palette_path),
            "-filter_complex",
            filter_complex,
            "-loop",
            str(args.loop),
            str(output_path),
        ]
    )
    return cmd


def convert_clip(
    clip: ClipSource,
    destination: Path,
    base_filters: str,
    args: argparse.Namespace,
) -> None:
    if args.dry_run:
        print(f"[DRY-RUN] {clip.path} -> {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)

    palette_filter = build_palette_filter(base_filters, args)
    filter_complex = build_filter_complex(base_filters, args)

    with tempfile.TemporaryDirectory(prefix="gif_palette_") as tmp_dir:
        palette_path = Path(tmp_dir) / f"{clip.path.stem}_palette.png"
        palette_cmd = build_palette_command(
            clip.path, palette_path, palette_filter, args
        )
        gif_cmd = build_gif_command(
            clip.path, palette_path, destination, filter_complex, args
        )
        run_command(palette_cmd, args.verbose)
        run_command(gif_cmd, args.verbose)


def main() -> None:
    args = parse_args()
    ensure_ffmpeg_available()
    extensions = normalize_extensions(args.extensions)
    clips = collect_sources(args.inputs, extensions)

    if not clips:
        print("未找到可转换的视频文件。")
        sys.exit(1)

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    base_filters = build_base_filters(args)

    total = len(clips)
    success = 0
    skipped = 0
    failures: List[Tuple[Path, str]] = []

    for index, clip in enumerate(clips, start=1):
        destination = build_output_path(
            clip, output_dir, args.preserve_structure, args.suffix
        )
        if destination.exists() and not args.overwrite and not args.dry_run:
            skipped += 1
            print(f"[{index}/{total}] 已存在，跳过: {destination}")
            continue

        print(f"[{index}/{total}] 转换: {clip.path} -> {destination}")

        try:
            convert_clip(clip, destination, base_filters, args)
            success += 1
        except subprocess.CalledProcessError as exc:
            failures.append((clip.path, str(exc)))
            print(f"❌ 转换失败: {clip.path}")
        except Exception as exc:  # 捕获意外错误
            failures.append((clip.path, str(exc)))
            print(f"❌ 未预期错误: {clip.path} ({exc})")

    print("\n=== 处理完成 ===")
    print(f"成功: {success}")
    print(f"跳过: {skipped}")
    print(f"失败: {len(failures)}")

    if failures:
        print("\n失败列表：")
        for path, reason in failures:
            print(f"- {path}: {reason}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断。")
        sys.exit(130)
