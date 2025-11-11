"""
Utility for extracting structured information from Chinese VAT invoices using OCR.

This module offers a small pipeline:

1. Run OCR against an invoice image (PNG, JPG, etc.) using one of the supported engines
   (`paddleocr`, `easyocr`, or `pytesseract` – picked in that priority order if installed).
2. Apply a set of heuristics and regular expressions over the raw text lines to recover the
   most common key fields that appear on standard invoices.
3. Expose a CLI to process a file and emit JSON with both the structured fields and the
   captured raw lines for manual inspection.

Example:

```bash
python invoice_info_extractor.py example_invoice.jpg --json output.json
```
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

OCR_ENGINE_PRIORITY: Sequence[str] = ("paddleocr", "easyocr", "pytesseract")


class OCRNotAvailableError(RuntimeError):
    """Raised when no supported OCR engine is available in the environment."""


@dataclass
class OCRResult:
    text: str
    confidence: float
    position: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))


class InvoiceOCR:
    """Wraps one of the supported OCR engines and exposes a unified interface."""

    def __init__(
        self,
        lang: str = "ch",
        use_gpu: bool = False,
        min_score: float = 0.5,
        engine_priority: Sequence[str] = OCR_ENGINE_PRIORITY,
    ) -> None:
        self.lang = lang
        self.use_gpu = use_gpu
        self.min_score = min_score
        self.engine_name: Optional[str] = None
        self._engine = None
        self._init_engine(engine_priority)

    def _init_engine(self, engine_priority: Sequence[str]) -> None:
        last_error: Optional[Exception] = None
        for engine_name in engine_priority:
            try:
                init_method = getattr(self, f"_init_{engine_name}")
            except AttributeError:
                continue
            try:
                self._engine = init_method()
                self.engine_name = engine_name
                return
            except Exception as exc:  # pragma: no cover - failure paths are environment-specific
                last_error = exc
        raise OCRNotAvailableError(
            "No OCR engine is available. Install one of `paddleocr`, `easyocr`, or "
            "`pytesseract`. Last error: {}".format(last_error)
        ) from last_error

    # Individual engine initialisers -------------------------------------------------
    def _init_paddleocr(self):
        from paddleocr import PaddleOCR  # type: ignore

        # PaddleOCR uses language codes like "ch", "chinese_cht", "en" etc.
        lang = self.lang if self.lang in {"ch", "chinese_cht", "en"} else "ch"
        return PaddleOCR(use_angle_cls=True, use_gpu=self.use_gpu, lang=lang)

    def _init_easyocr(self):
        import easyocr  # type: ignore

        # easyocr expects list of languages; 'ch_sim' covers simplified Chinese.
        langs = ["ch_sim", "en"] if self.lang.startswith("ch") else ["en"]
        return easyocr.Reader(langs, gpu=self.use_gpu)

    def _init_pytesseract(self):
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore

        # Keep references on the instance for later use
        self._pytesseract = pytesseract
        self._pil_image = Image
        return "pytesseract"

    # -------------------------------------------------------------------------------
    def read(self, file_path: str) -> List[OCRResult]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        if self.engine_name == "paddleocr":
            return self._read_with_paddleocr(file_path)
        if self.engine_name == "easyocr":
            return self._read_with_easyocr(file_path)
        if self.engine_name == "pytesseract":
            return self._read_with_pytesseract(file_path)
        raise RuntimeError("Unexpected OCR engine state")

    def _read_with_paddleocr(self, file_path: str) -> List[OCRResult]:
        results: List[OCRResult] = []
        ocr_pages = self._engine.ocr(file_path, cls=True)
        for page in ocr_pages:
            for line in page:
                box, (text, confidence) = line
                if confidence < self.min_score:
                    continue
                top = min(point[1] for point in box)
                left = min(point[0] for point in box)
                results.append(OCRResult(text=text.strip(), confidence=float(confidence), position=(top, left)))
        results.sort(key=lambda item: (round(item.position[0] / 10.0), item.position[0], item.position[1]))
        return results

    def _read_with_easyocr(self, file_path: str) -> List[OCRResult]:
        results: List[OCRResult] = []
        ocr_lines = self._engine.readtext(file_path, detail=1)
        for box, text, confidence in ocr_lines:
            if confidence < self.min_score:
                continue
            top = min(point[1] for point in box)
            left = min(point[0] for point in box)
            results.append(OCRResult(text=text.strip(), confidence=float(confidence), position=(top, left)))
        results.sort(key=lambda item: (round(item.position[0] / 10.0), item.position[0], item.position[1]))
        return results

    def _read_with_pytesseract(self, file_path: str) -> List[OCRResult]:
        img = self._pil_image.open(file_path)
        lang = "chi_sim+eng" if self.lang.startswith("ch") else "eng"
        data = self._pytesseract.image_to_data(img, lang=lang, output_type=self._pytesseract.Output.DICT)
        results: List[OCRResult] = []
        for text, conf, top, left in zip(data["text"], data["conf"], data["top"], data["left"]):
            if not text or text.isspace():
                continue
            try:
                conf_value = float(conf)
            except ValueError:
                conf_value = -1.0
            if conf_value < self.min_score * 100:
                continue
            results.append(OCRResult(text=text.strip(), confidence=conf_value / 100.0, position=(float(top), float(left))))
        results.sort(key=lambda item: (round(item.position[0] / 10.0), item.position[0], item.position[1]))
        return results


# -------------------------------- Parsing utilities --------------------------------
COLON_VARIANTS = ("：", ":", "：", "﹕", "﹕", "﹕")


def _normalise_text(line: str) -> str:
    line = line.strip()
    for colon in COLON_VARIANTS:
        line = line.replace(colon, ":")
    return re.sub(r"\s+", " ", line)


def _extract_value_after_keyword(lines: Sequence[str], keywords: Sequence[str]) -> Optional[str]:
    for idx, line in enumerate(lines):
        for keyword in keywords:
            if keyword in line:
                remainder = line.split(keyword, 1)[-1]
                remainder = remainder.split(":", 1)[-1] if ":" in remainder else remainder
                value = remainder.strip(" ：:,-")
                if value:
                    return value
                # Fallback to next line if the current line only contains the keyword
                if idx + 1 < len(lines):
                    candidate = lines[idx + 1].strip(" ：:,-")
                    if candidate:
                        return candidate
    return None


def _maybe_parse_amount(value: str) -> Optional[float]:
    cleaned = value.replace("¥", "").replace("￥", "").replace("元", "")
    cleaned = cleaned.replace(",", "").replace(" ", "")
    match = re.search(r"(-?\d+(?:\.\d{1,2})?)", cleaned)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _maybe_parse_date(value: str) -> Optional[str]:
    candidate = value.strip()
    if not candidate:
        return None
    candidate = candidate.replace("年", "-").replace("月", "-").replace("日", "")
    candidate = candidate.replace("/", "-").replace(".", "-")
    candidate = re.sub(r"-+", "-", candidate)
    for fmt in ("%Y-%m-%d", "%Y-%m-%d", "%y-%m-%d"):
        try:
            dt = datetime.strptime(candidate, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


FIELD_PATTERNS: Dict[str, Sequence[str]] = {
    "invoice_code": (
        r"发票代码[: ]*([0-9]{10,12})",
        r"代码[: ]*([0-9]{10,12})",
    ),
    "invoice_number": (
        r"发票号码[: ]*([0-9]{8,12})",
        r"号码[: ]*([0-9]{8,12})",
    ),
    "issue_date": (
        r"开票日期[: ]*([0-9]{4}[年/-][0-9]{1,2}[月/-][0-9]{1,2}日?)",
        r"开票日期[: ]*([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})",
    ),
    "machine_code": (r"机器编号[: ]*([0-9]{8,18})",),
    "verification_code": (
        r"校验码[: ]*([0-9]{6,20})",
        r"验证码[: ]*([0-9]{6,20})",
    ),
    "amount_excluding_tax": (
        r"(?:合计|金额|小写)[: ]*([0-9,.]+)",
        r"金额合计[: ]*([0-9,.]+)",
    ),
    "total_tax": (
        r"税额[: ]*([0-9,.]+)",
        r"税金[: ]*([0-9,.]+)",
    ),
    "total_amount": (
        r"(?:价税合计|合计|合计人民币)[: ]*([0-9,.]+)",
    ),
}

KEYWORD_FIELDS: Dict[str, Sequence[str]] = {
    "purchaser_name": ("购买方名称", "购货单位", "购方名称", "购买单位", "受票方名称"),
    "purchaser_tax_id": ("购方税号", "购买方税号", "购方纳税人识别号", "购方识别号", "购方税务登记号"),
    "seller_name": ("销售方名称", "销售单位", "销方名称", "销货单位"),
    "seller_tax_id": ("销方税号", "销售方税号", "销方纳税人识别号", "销方识别号"),
    "remarks": ("备注",),
}


@dataclass
class InvoiceMetadata:
    raw_lines: List[str]
    fields: Dict[str, object]
    engine_used: str


class InvoiceFieldParser:
    """Extract key invoice fields from recognised text lines."""

    def parse(self, lines: Iterable[OCRResult]) -> InvoiceMetadata:
        ordered_lines = [_normalise_text(item.text) for item in lines if item.text.strip()]
        blob = "\n".join(ordered_lines)
        fields: Dict[str, object] = {}

        for key, patterns in FIELD_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, blob)
                if match:
                    value = match.group(1).strip()
                    if key == "issue_date":
                        parsed = _maybe_parse_date(value)
                        fields[key] = parsed or value
                    elif key in {"amount_excluding_tax", "total_tax", "total_amount"}:
                        amount = _maybe_parse_amount(value)
                        fields[key] = amount if amount is not None else value
                    else:
                        fields[key] = value
                    break

        for key, keywords in KEYWORD_FIELDS.items():
            value = _extract_value_after_keyword(ordered_lines, keywords)
            if value:
                if key in {"purchaser_tax_id", "seller_tax_id"}:
                    value = re.sub(r"[^0-9A-Z]", "", value)
                fields[key] = value

        # Attempt to detect the totals from lines if not captured by regex (fallback)
        if "total_amount" not in fields:
            fallback_total = _extract_value_after_keyword(ordered_lines, ("价税合计", "合计"))
            if fallback_total:
                amount = _maybe_parse_amount(fallback_total)
                fields["total_amount"] = amount if amount is not None else fallback_total

        return InvoiceMetadata(raw_lines=ordered_lines, fields=fields, engine_used="")


def extract_invoice_info(file_path: str, use_gpu: bool = False, min_score: float = 0.5) -> InvoiceMetadata:
    ocr = InvoiceOCR(use_gpu=use_gpu, min_score=min_score)
    ocr_results = ocr.read(file_path)
    parser = InvoiceFieldParser()
    metadata = parser.parse(ocr_results)
    metadata.engine_used = ocr.engine_name or "unknown"
    return metadata


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract structured information from a Chinese invoice image.")
    parser.add_argument("file", help="Path to the invoice image (e.g., JPG, PNG).")
    parser.add_argument("--json", dest="json_path", help="Optional path to write the extracted metadata as JSON.")
    parser.add_argument("--use-gpu", action="store_true", help="Attempt to run OCR on GPU when supported.")
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.5,
        help="Discard OCR detections with confidence below this threshold (default: 0.5).",
    )
    parser.add_argument(
        "--engine",
        choices=list(OCR_ENGINE_PRIORITY),
        nargs="*",
        help="Override the OCR engine priority order. Provide one or multiple engine names.",
    )
    return parser


def _serialise_metadata(metadata: InvoiceMetadata) -> Dict[str, object]:
    return {
        "engine": metadata.engine_used,
        "fields": metadata.fields,
        "raw_lines": metadata.raw_lines,
    }


def main() -> None:
    parser = _build_cli_parser()
    args = parser.parse_args()
    engine_priority: Sequence[str] = tuple(args.engine) if args.engine else OCR_ENGINE_PRIORITY

    invoice_ocr = InvoiceOCR(use_gpu=args.use_gpu, min_score=args.min_score, engine_priority=engine_priority)
    ocr_results = invoice_ocr.read(args.file)
    field_parser = InvoiceFieldParser()
    metadata = field_parser.parse(ocr_results)
    metadata.engine_used = invoice_ocr.engine_name or "unknown"

    result = _serialise_metadata(metadata)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
