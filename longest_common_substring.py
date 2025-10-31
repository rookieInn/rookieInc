#!/usr/bin/env python3
"""Utility functions for finding the longest common substring between two texts.

This module exposes a dynamic-programming based implementation that can handle
large input strings efficiently by keeping only two rows of the DP matrix in
memory. A small command line interface is provided so the script can be invoked
directly to analyse two text snippets or files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional
import argparse
import sys


@dataclass(frozen=True)
class SubstringMatch:
    """Represents one longest common substring match between two texts."""

    substring: str
    start_in_text1: int
    start_in_text2: int
    length: int


def longest_common_substrings(
    text1: str, text2: str, *, ignore_case: bool = False
) -> List[SubstringMatch]:
    """Return every longest common substring shared by *text1* and *text2*.

    Args:
        text1: The first text snippet.
        text2: The second text snippet.
        ignore_case: When True the comparison is case-insensitive (casefold is
            used), but the returned substring preserves the original casing from
            *text1*.

    Returns:
        A list of SubstringMatch objects sorted by the starting index within
        *text1*. An empty list is returned when the texts have no common
        substring.
    """

    if not text1 or not text2:
        return []

    seq1 = text1.casefold() if ignore_case else text1
    seq2 = text2.casefold() if ignore_case else text2

    previous_row = [0] * (len(seq2) + 1)
    longest_length = 0
    end_positions: List[tuple[int, int]] = []

    for index1, char1 in enumerate(seq1, start=1):
        current_row = [0] * (len(seq2) + 1)
        for index2, char2 in enumerate(seq2, start=1):
            if char1 == char2:
                current_row[index2] = previous_row[index2 - 1] + 1
                if current_row[index2] > longest_length:
                    longest_length = current_row[index2]
                    end_positions = [(index1, index2)]
                elif current_row[index2] == longest_length and longest_length > 0:
                    end_positions.append((index1, index2))
        previous_row = current_row

    if longest_length == 0:
        return []

    matches: List[SubstringMatch] = []
    seen: set[tuple[int, int]] = set()
    for end_index1, end_index2 in end_positions:
        start1 = end_index1 - longest_length
        start2 = end_index2 - longest_length
        key = (start1, start2)
        if key in seen:
            continue
        seen.add(key)
        substring = text1[start1:end_index1]
        matches.append(
            SubstringMatch(
                substring=substring,
                start_in_text1=start1,
                start_in_text2=start2,
                length=longest_length,
            )
        )

    matches.sort(key=lambda match: (match.start_in_text1, match.start_in_text2))
    return matches


def longest_common_substring(
    text1: str, text2: str, *, ignore_case: bool = False
) -> Optional[SubstringMatch]:
    """Return a single longest common substring between *text1* and *text2*.

    This is a convenience wrapper around :func:`longest_common_substrings`
    returning only the first match (or ``None`` when the inputs do not share any
    substring).
    """

    matches = longest_common_substrings(text1, text2, ignore_case=ignore_case)
    return matches[0] if matches else None


def _load_texts_from_args(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve the two input texts according to parsed CLI arguments."""

    if args.file1 or args.file2:
        if not args.file1 or not args.file2:
            raise SystemExit("When using --file1/--file2 you must provide both paths.")
        try:
            text1 = Path(args.file1).read_text(encoding=args.encoding)
            text2 = Path(args.file2).read_text(encoding=args.encoding)
        except OSError as exc:  # pragma: no cover - bubble up for CLI usage
            raise SystemExit(f"Failed to read files: {exc}")
        return text1, text2

    if args.text1 is None or args.text2 is None:
        raise SystemExit("Provide either two positional texts or two file paths.")

    return args.text1, args.text2


def build_arg_parser() -> argparse.ArgumentParser:
    """Create and configure the ArgumentParser for CLI usage."""

    parser = argparse.ArgumentParser(
        description=(
            "Find the longest common substring between two text snippets or files."
        )
    )
    parser.add_argument("text1", nargs="?", help="First text snippet")
    parser.add_argument("text2", nargs="?", help="Second text snippet")
    parser.add_argument("--file1", help="Path to the first input file")
    parser.add_argument("--file2", help="Path to the second input file")
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding used when reading from files (default: utf-8)",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Perform a case-insensitive comparison",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Print every longest common substring instead of only the first",
    )
    return parser


def _main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    text1, text2 = _load_texts_from_args(args)
    matches = longest_common_substrings(text1, text2, ignore_case=args.ignore_case)

    if not matches:
        print("No common substring found.")
        return 1

    if args.show_all:
        for match in matches:
            print(
                f"Substring: {match.substring!r}\n"
                f"Length: {match.length}\n"
                f"text1 index: {match.start_in_text1}\n"
                f"text2 index: {match.start_in_text2}\n"
            )
    else:
        match = matches[0]
        print(
            f"Substring: {match.substring!r}\n"
            f"Length: {match.length}\n"
            f"text1 index: {match.start_in_text1}\n"
            f"text2 index: {match.start_in_text2}"
        )

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(_main())

