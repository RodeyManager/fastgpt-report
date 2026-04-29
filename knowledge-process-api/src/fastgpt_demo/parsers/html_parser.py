"""HTML parser — 使用 BeautifulSoup 提取文本和结构化内容。"""

from __future__ import annotations

import chardet
from bs4 import BeautifulSoup

from ._types import ParseResult


def parse(buffer: bytes, **kwargs) -> ParseResult:
    """解析 HTML 文件，提取纯文本和结构化 HTML 预览。

    - raw_text: 原始 HTML 内容（供 Markdown 转换器 html_to_markdown 使用）
    - format_text: 原始 HTML 内容（与 raw_text 一致）
    - html_preview: 结构化 HTML（soup.body 或整个文档）
    """

    # 编码检测：先尝试 UTF-8 严格解码，失败则用 chardet 检测的编码
    try:
        html_str = buffer.decode("utf-8")
    except UnicodeDecodeError:
        detection = chardet.detect(buffer)
        fallback_encoding: str = detection.get("encoding") or "utf-8"
        html_str = buffer.decode(fallback_encoding, errors="replace")

    # 解析 HTML 并提取结构化内容
    soup = BeautifulSoup(html_str, "html.parser")

    # 原始 HTML 内容（供 converter 中的 html_to_markdown 使用）
    raw_text = str(soup)

    # 结构化 HTML 预览（仅 body 部分，或整个文档）
    html_preview = str(soup.body) if soup.body else str(soup)

    return ParseResult(
        raw_text=raw_text,
        format_text=raw_text,
        html_preview=html_preview,
        image_list=[],
    )
