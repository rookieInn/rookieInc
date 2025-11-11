#!/usr/bin/env python3
"""
Utility for combining multiple images into a single collage.

Supported layouts:
    - long: stack images vertically to form a long image.
    - horizontal: place images side-by-side in a single row.
    - grid: specify layouts like 2x2, 3x1, etc. using the pattern <cols>x<rows>.

Spacing between images and outer margins can be customised, and callers can
choose either a solid background colour or provide a background image to fill
the canvas.
"""

from __future__ import annotations

import argparse
import math
import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageColor


@dataclass(frozen=True)
class LayoutSpec:
    """Represents the resolved layout configuration."""

    columns: int
    rows: int


class LayoutParseError(ValueError):
    """Raised when the passed layout string cannot be parsed."""


def _parse_layout(layout: str, image_count: int) -> LayoutSpec:
    """
    Parse a layout string into a LayoutSpec.

    Parameters
    ----------
    layout:
        Layout string. Supported values:
            - "long" / "vertical": single column, all images stacked vertically.
            - "horizontal": single row, all images in one row.
            - "<cols>x<rows>" or "<cols>*<rows>": explicit grid definition.
    image_count:
        Number of images that will be placed in the collage.

    Returns
    -------
    LayoutSpec

    Raises
    ------
    LayoutParseError
        If the layout string is invalid or specifies non-positive dimensions.
    """

    if image_count <= 0:
        raise LayoutParseError("At least one image is required to build a collage.")

    normalized = layout.strip().lower()

    if normalized in {"long", "vertical"}:
        return LayoutSpec(columns=1, rows=image_count)

    if normalized in {"horizontal"}:
        return LayoutSpec(columns=image_count, rows=1)

    grid_match = re.fullmatch(r"(\d+)\s*[x\*]\s*(\d+)", normalized)
    if grid_match:
        columns = int(grid_match.group(1))
        rows = int(grid_match.group(2))

        if columns <= 0 or rows <= 0:
            raise LayoutParseError(
                f"Layout '{layout}' specifies non-positive dimensions."
            )

        rows = max(rows, math.ceil(image_count / columns))
        return LayoutSpec(columns=columns, rows=rows)

    raise LayoutParseError(
        f"Unrecognised layout '{layout}'. "
        "Supported formats: 'long', 'horizontal', or '<cols>x<rows>' (e.g. 2x2, 3x1)."
    )


def _load_images(image_paths: Sequence[str]) -> List[Image.Image]:
    """Load images from the provided paths."""
    images: List[Image.Image] = []
    for path in image_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")

        image = Image.open(path).convert("RGBA")
        images.append(image)
    return images


def _parse_background_colour(colour: str | None) -> Tuple[int, int, int, int]:
    """Convert a colour string into an RGBA tuple."""
    if colour is None:
        return 255, 255, 255, 255

    try:
        rgba = ImageColor.getcolor(colour, "RGBA")
    except ValueError as exc:
        raise ValueError(f"Invalid background colour '{colour}'.") from exc

    if len(rgba) == 3:
        return rgba + (255,)
    return rgba


def _prepare_background(
    width: int,
    height: int,
    colour: str | None,
    background_image: str | None,
) -> Image.Image:
    """
    Create the background canvas.

    If a background image is supplied it is resized to fit the target canvas
    dimensions. Otherwise a solid colour background is created.
    """

    if background_image:
        if not os.path.exists(background_image):
            raise FileNotFoundError(f"Background image not found: {background_image}")

        bg = Image.open(background_image).convert("RGBA")
        if bg.size != (width, height):
            bg = bg.resize((width, height), Image.Resampling.LANCZOS)
        return bg

    return Image.new("RGBA", (width, height), _parse_background_colour(colour))


def combine_images(
    image_paths: Sequence[str],
    *,
    layout: str = "long",
    spacing: int = 0,
    margin: int = 0,
    background_colour: str | None = "#FFFFFF",
    background_image: str | None = None,
    output_path: str | None = None,
) -> Image.Image:
    """
    Combine multiple images into a single image using the specified layout.

    Parameters
    ----------
    image_paths:
        Paths to input images in the order they should appear.
    layout:
        Layout definition. Supports "long", "horizontal", or grid definitions
        such as "2x2" / "3x1".
    spacing:
        Space in pixels between adjacent images.
    margin:
        Outer padding in pixels applied around the entire collage.
    background_colour:
        Background colour (hex code, colour name, etc.). Ignored when
        ``background_image`` is provided.
    background_image:
        Path to an image used as the background. It will be resized to match the
        output dimensions.
    output_path:
        Optional file path to save the resulting image. If omitted, the image is
        returned but not written to disk.

    Returns
    -------
    Image.Image
        The composed collage image.
    """

    if not image_paths:
        raise ValueError("At least one image path must be provided.")

    if spacing < 0:
        raise ValueError("Spacing must be zero or a positive integer.")

    if margin < 0:
        raise ValueError("Margin must be zero or a positive integer.")

    images = _load_images(image_paths)
    layout_spec = _parse_layout(layout, len(images))

    columns = layout_spec.columns
    rows = layout_spec.rows

    column_widths = [0 for _ in range(columns)]
    row_heights = [0 for _ in range(rows)]

    for index, image in enumerate(images):
        row = index // columns
        col = index % columns

        if row >= rows:
            raise RuntimeError(
                "Calculated row index exceeds layout bounds. "
                "This indicates an internal layout computation error."
            )

        column_widths[col] = max(column_widths[col], image.width)
        row_heights[row] = max(row_heights[row], image.height)

    total_width = sum(column_widths) + spacing * (columns - 1 if columns > 1 else 0)
    total_height = sum(row_heights) + spacing * (rows - 1 if rows > 1 else 0)

    canvas_width = total_width + margin * 2
    canvas_height = total_height + margin * 2

    canvas = _prepare_background(
        canvas_width,
        canvas_height,
        background_colour,
        background_image,
    )

    col_offsets: List[int] = []
    x_pointer = margin
    for width in column_widths:
        col_offsets.append(x_pointer)
        x_pointer += width + spacing

    row_offsets: List[int] = []
    y_pointer = margin
    for height in row_heights:
        row_offsets.append(y_pointer)
        y_pointer += height + spacing

    for index, image in enumerate(images):
        row = index // columns
        col = index % columns

        base_x = col_offsets[col]
        base_y = row_offsets[row]

        x_offset = base_x + (column_widths[col] - image.width) // 2
        y_offset = base_y + (row_heights[row] - image.height) // 2

        canvas.paste(image, (int(x_offset), int(y_offset)), image)

    if output_path:
        canvas.save(output_path)

    return canvas


def build_argument_parser() -> argparse.ArgumentParser:
    """Create an argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Combine multiple images into a collage with flexible layouts.",
    )
    parser.add_argument(
        "images",
        nargs="+",
        help="Input image paths in the order they should appear.",
    )
    parser.add_argument(
        "-l",
        "--layout",
        default="long",
        help="Layout definition: 'long', 'horizontal', or '<cols>x<rows>' "
        "(e.g. 2x2, 3x1).",
    )
    parser.add_argument(
        "-s",
        "--spacing",
        type=int,
        default=0,
        help="Spacing in pixels between images (default: 0).",
    )
    parser.add_argument(
        "-m",
        "--margin",
        type=int,
        default=0,
        help="Outer margin in pixels around the collage (default: 0).",
    )
    parser.add_argument(
        "--background-colour",
        default="#FFFFFF",
        help="Background colour (hex or name). Ignored if --background-image is used.",
    )
    parser.add_argument(
        "--background-image",
        help="Path to an image used as the background. Resized to fit the collage.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to the output image file.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    """Command-line interface entry point."""
    parser = build_argument_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    combine_images(
        args.images,
        layout=args.layout,
        spacing=args.spacing,
        margin=args.margin,
        background_colour=args.background_colour,
        background_image=args.background_image,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
