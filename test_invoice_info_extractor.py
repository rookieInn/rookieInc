import pytest

from invoice_info_extractor import InvoiceFieldParser, OCRResult


def _ocr_line(text: str, confidence: float = 0.99, top: float = 0.0, left: float = 0.0) -> OCRResult:
    return OCRResult(text=text, confidence=confidence, position=(top, left))


def test_parser_extracts_core_fields():
    parser = InvoiceFieldParser()
    lines = [
        _ocr_line("发票代码：044031900211"),
        _ocr_line("发票号码:12345678"),
        _ocr_line("开票日期：2024年09月01日"),
        _ocr_line("购货单位：某某科技有限公司"),
        _ocr_line("购方税号：1234567890"),
        _ocr_line("销售方名称：北京某公司"),
        _ocr_line("销方税号：987654321"),
        _ocr_line("价税合计：¥1,234.56"),
        _ocr_line("税额：123.45"),
        _ocr_line("合计：1,111.11"),
        _ocr_line("备注：本发票由系统自动开具"),
    ]

    metadata = parser.parse(lines)

    assert metadata.fields["invoice_code"] == "044031900211"
    assert metadata.fields["invoice_number"] == "12345678"
    assert metadata.fields["issue_date"] == "2024-09-01"
    assert metadata.fields["purchaser_name"] == "某某科技有限公司"
    assert metadata.fields["purchaser_tax_id"] == "1234567890"
    assert metadata.fields["seller_name"] == "北京某公司"
    assert metadata.fields["seller_tax_id"] == "987654321"
    assert metadata.fields["remarks"] == "本发票由系统自动开具"
    assert metadata.fields["total_tax"] == pytest.approx(123.45)
    assert metadata.fields["amount_excluding_tax"] == pytest.approx(1111.11)
    assert metadata.fields["total_amount"] == pytest.approx(1234.56)


def test_keyword_lookup_uses_following_line():
    parser = InvoiceFieldParser()
    lines = [
        _ocr_line("销售方名称"),
        _ocr_line("上海示例有限公司"),
        _ocr_line("购方税号"),
        _ocr_line("  91320104551234567R  "),
    ]

    metadata = parser.parse(lines)

    assert metadata.fields["seller_name"] == "上海示例有限公司"
    assert metadata.fields["purchaser_tax_id"] == "91320104551234567R"
