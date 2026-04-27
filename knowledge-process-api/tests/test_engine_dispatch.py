import io

from src.fastgpt_demo.parsers import parse_file
from src.fastgpt_demo.parsers._types import ParseResult
from src.fastgpt_demo.parsers.mineru_parser import parse as parse_mineru


FIXTURES = "tests/fixtures"


def _read(name):
    with open(f"{FIXTURES}/{name}", "rb") as f:
        return f.read()


# --- engine dispatch via parse_file ---


def test_default_engine_uses_fastgpt():
    buf = _read("test.pdf")
    result = parse_file(buf, "test.pdf")
    assert isinstance(result, ParseResult)
    assert result.raw_text is not None


def test_explicit_fastgpt_same_as_default():
    buf = _read("test.pdf")
    default = parse_file(buf, "test.pdf")
    explicit = parse_file(buf, "test.pdf", engine="fastgpt")
    assert default.raw_text == explicit.raw_text


def test_mineru_engine_pdf():
    buf = _read("test.pdf")
    result = parse_file(buf, "test.pdf", engine="mineru")
    assert isinstance(result, ParseResult)
    assert "MinerU" in result.raw_text


def test_mineru_unsupported_csv():
    buf = _read("test.csv")
    import pytest
    with pytest.raises(ValueError, match="MinerU does not support"):
        parse_file(buf, "test.csv", engine="mineru")


def test_mineru_unsupported_xlsx():
    import pytest
    with pytest.raises(ValueError, match="MinerU does not support"):
        parse_file(b"", "data.xlsx", engine="mineru")


def test_mineru_unsupported_txt():
    import pytest
    with pytest.raises(ValueError, match="MinerU does not support"):
        parse_file(b"hello", "readme.txt", engine="mineru")


def test_fastgpt_unknown_extension():
    import pytest
    with pytest.raises(ValueError, match="Unsupported file extension"):
        parse_file(b"data", "file.xyz")


# --- mineru client unit tests ---


def test_placeholder_returns_parse_result():
    result = parse_mineru(b"fake pdf bytes", "doc.pdf")
    assert isinstance(result, ParseResult)


def test_placeholder_has_all_fields():
    result = parse_mineru(b"bytes", "doc.pdf")
    assert isinstance(result.raw_text, str) and len(result.raw_text) > 0
    assert isinstance(result.format_text, str) and len(result.format_text) > 0
    assert isinstance(result.html_preview, str) and len(result.html_preview) > 0
    assert isinstance(result.image_list, list)
    assert result.sheet_names is None


def test_placeholder_raw_text_contains_mineru():
    result = parse_mineru(b"bytes", "report.pdf")
    assert "MinerU" in result.raw_text
    assert "report.pdf" in result.raw_text
