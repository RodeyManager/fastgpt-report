"""OpenDataLoader-PDF 解析器单元测试和集成测试。"""

import pytest

from src.fastgpt_demo.parsers import parse_file
from src.fastgpt_demo.parsers._types import ParseResult
from src.fastgpt_demo.parsers.opendataloader_pdf_parser import (
    parse_opendataloader_pdf,
)

FIXTURES = "tests/fixtures"


def _docling_available():
    """检测 Docling 库是否可用且能正常解析 PDF"""
    try:
        import io
        from docling.datamodel.base_models import DocumentStream
        from docling.document_converter import DocumentConverter

        # 创建一个最小的测试 PDF
        test_pdf = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000214 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n312\n%%EOF\n'

        buf = io.BytesIO(test_pdf)
        source = DocumentStream(name='test.pdf', stream=buf)
        converter = DocumentConverter()
        result = converter.convert(source)
        return result.status.value == "success"
    except Exception:
        return False


docling_available = pytest.mark.skipif(
    not _docling_available(),
    reason="Docling 库不可用或无法解析 PDF",
)


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
