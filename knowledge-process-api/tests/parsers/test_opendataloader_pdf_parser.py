"""OpenDataLoader-PDF 解析器单元测试和集成测试。"""

import pytest
import httpx

from src.fastgpt_demo.parsers import parse_file
from src.fastgpt_demo.parsers._types import ParseResult
from src.fastgpt_demo.parsers.opendataloader_pdf_parser import (
    _extract_texts,
    _extract_tables_as_markdown,
    parse_opendataloader_pdf,
)

FIXTURES = "tests/fixtures"


def _docling_available():
    """检测 Docling Server 是否可用"""
    try:
        resp = httpx.get("http://localhost:5002/health", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


docling_available = pytest.mark.skipif(
    not _docling_available(),
    reason="Docling Server (localhost:5002) 不可用",
)


# --- _extract_texts 单元测试 ---


class TestExtractTexts:
    def test_empty_doc(self):
        result = _extract_texts({"texts": []})
        assert result == ""

    def test_single_text(self):
        doc = {
            "texts": [
                {"text": "Hello World", "prov": [{"page_no": 1, "bbox": {}}]}
            ]
        }
        result = _extract_texts(doc)
        assert "Hello World" in result

    def test_multiple_pages(self):
        doc = {
            "texts": [
                {"text": "Page 1 text", "prov": [{"page_no": 1, "bbox": {}}]},
                {"text": "Page 2 text", "prov": [{"page_no": 2, "bbox": {}}]},
            ]
        }
        result = _extract_texts(doc)
        assert "Page 1 text" in result
        assert "Page 2 text" in result
        assert "\n\n" in result

    def test_skips_empty_text(self):
        doc = {
            "texts": [
                {"text": "Valid", "prov": [{"page_no": 1, "bbox": {}}]},
                {"text": "", "prov": [{"page_no": 1, "bbox": {}}]},
            ]
        }
        result = _extract_texts(doc)
        assert result == "Valid"

    def test_no_prov_skipped(self):
        doc = {"texts": [{"text": "No provenance", "prov": []}]}
        result = _extract_texts(doc)
        assert result == ""


# --- _extract_tables_as_markdown 单元测试 ---


class TestExtractTables:
    def test_empty_tables(self):
        result = _extract_tables_as_markdown({"tables": []})
        assert result == ""

    def test_single_table(self):
        doc = {
            "tables": [
                {
                    "data": [
                        [{"text": "Name"}, {"text": "Age"}],
                        [{"text": "Alice"}, {"text": "30"}],
                    ]
                }
            ]
        }
        result = _extract_tables_as_markdown(doc)
        assert "| Name | Age |" in result
        assert "| Alice | 30 |" in result
        assert "| ---" in result

    def test_empty_data(self):
        doc = {"tables": [{"data": []}]}
        result = _extract_tables_as_markdown(doc)
        assert result == ""


# --- parse_file 分派逻辑测试 ---


class TestOpenLoaderDispatch:
    def test_non_pdf_rejected(self):
        """非 PDF 文件使用 opendataloader-pdf 引擎应被拒绝"""
        with pytest.raises(ValueError, match="仅支持 PDF"):
            parse_file(b"fake-content", "test.docx", engine="opendataloader-pdf")

    def test_non_pdf_html_rejected(self):
        """HTML 文件使用 opendataloader-pdf 引擎应被拒绝"""
        with pytest.raises(ValueError, match="仅支持 PDF"):
            parse_file(b"<html></html>", "test.html", engine="opendataloader-pdf")


# --- 集成测试（需 Docling Server 运行）---


@docling_available
class TestParseOpenDataLoaderPdfIntegration:
    def test_parse_success(self):
        with open(f"{FIXTURES}/test.pdf", "rb") as f:
            buffer = f.read()

        result = parse_opendataloader_pdf(buffer, timeout=120)
        assert isinstance(result, ParseResult)
        assert isinstance(result.raw_text, str)
        assert isinstance(result.format_text, str)

    def test_parse_with_image_list(self):
        with open(f"{FIXTURES}/test.pdf", "rb") as f:
            buffer = f.read()

        result = parse_opendataloader_pdf(buffer, timeout=120)
        assert isinstance(result, ParseResult)
        assert isinstance(result.image_list, list)

    def test_parse_via_dispatch(self):
        """通过 parse_file 分派调用 opendataloader-pdf 引擎"""
        with open(f"{FIXTURES}/test.pdf", "rb") as f:
            buffer = f.read()

        result = parse_file(buffer, "test.pdf", engine="opendataloader-pdf")
        assert isinstance(result, ParseResult)
        assert isinstance(result.raw_text, str)
