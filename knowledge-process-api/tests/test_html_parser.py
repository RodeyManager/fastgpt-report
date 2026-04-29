"""HTML parser 单元测试和端到端测试。"""

import pytest

from src.fastgpt_demo.parsers import parse_file
from src.fastgpt_demo.parsers._types import ParseResult
from src.fastgpt_demo.parsers.html_parser import parse as parse_html


FIXTURES = "tests/fixtures"


def _read(name):
    with open(f"{FIXTURES}/{name}", "rb") as f:
        return f.read()


# --- 单元测试 ---


def test_parse_simple_html():
    """简单 HTML 解析，验证 raw_text 包含 HTML 标签内容。"""
    html = b"<html><body><h1>Hello</h1><p>World</p></body></html>"
    result = parse_html(html)

    assert isinstance(result, ParseResult)
    assert "<h1>Hello</h1>" in result.raw_text
    assert "<p>World</p>" in result.raw_text
    assert result.image_list == []
    assert result.sheet_names is None


def test_parse_html_with_encoding():
    """非 UTF-8 编码 HTML（GBK）应正确解码。"""
    html_str = "<html><body><p>你好世界</p></body></html>"
    html_bytes = html_str.encode("gbk")
    result = parse_html(html_bytes)

    assert "你好世界" in result.raw_text


def test_parse_empty_html():
    """空 HTML 文件不应报错。"""
    result = parse_html(b"")

    assert isinstance(result, ParseResult)
    assert result.raw_text is not None
    assert result.format_text is not None


def test_parse_html_with_tables():
    """包含表格的 HTML 应保留表格结构。"""
    html = b"""<html><body>
    <table>
        <tr><th>A</th><th>B</th></tr>
        <tr><td>1</td><td>2</td></tr>
    </table>
    </body></html>"""
    result = parse_html(html)

    assert "<table>" in result.raw_text
    assert "<th>A</th>" in result.raw_text
    assert "<td>1</td>" in result.raw_text
    assert "A" in result.raw_text
    assert "1" in result.raw_text


def test_raw_text_is_html_string():
    """raw_text 必须是 HTML 字符串（供 converter 使用）。"""
    html = b"<html><body><h1>Title</h1></body></html>"
    result = parse_html(html)

    assert result.raw_text.startswith("<html>")
    assert result.format_text == result.raw_text


def test_html_preview_is_body():
    """html_preview 应是 body 部分的 HTML。"""
    html = b"<html><head><title>T</title></head><body><p>Hello</p></body></html>"
    result = parse_html(html)

    assert "<body>" in result.html_preview
    assert "<p>Hello</p>" in result.html_preview
    assert "<head>" not in result.html_preview


# --- 路由分派测试 ---


def test_extension_dispatch_html():
    """.html 扩展名正确路由到 html parser。"""
    buf = _read("test.html")
    result = parse_file(buf, "test.html")

    assert isinstance(result, ParseResult)
    assert "标题一" in result.raw_text
    assert "这是第一个段落" in result.raw_text


def test_extension_dispatch_htm():
    """.htm 扩展名也能正确路由到 html parser。"""
    buf = _read("test.html")
    result = parse_file(buf, "test.htm")

    assert isinstance(result, ParseResult)
    assert "标题一" in result.raw_text


def test_method_html():
    """method=html 参数应直接调用 html parser。"""
    html = b"<html><body><p>Direct method</p></body></html>"
    result = parse_file(html, "data.bin", method="html")

    assert "Direct method" in result.raw_text


# --- 端到端测试（通过 FastAPI TestClient）---


def test_parse_html_via_api(client):
    """通过 FastAPI TestClient 端到端测试 HTML 上传解析。"""
    html_content = b"<html><body><h1>API Test</h1><p>Content here</p></body></html>"

    response = client.post(
        "/api/parse",
        files={"file": ("test.html", html_content, "text/html")},
        data={"method": "auto"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "<h1>API Test</h1>" in data["raw_text"]
    assert "<p>Content here</p>" in data["raw_text"]
    assert data["image_list"] == []


def test_parse_html_fixture_via_api(client):
    """通过 API 上传 test.html fixture 文件。"""
    buf = _read("test.html")

    response = client.post(
        "/api/parse",
        files={"file": ("test.html", buf, "text/html")},
        data={"method": "auto"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "标题一" in data["raw_text"]
    assert "这是第一个段落" in data["raw_text"]
