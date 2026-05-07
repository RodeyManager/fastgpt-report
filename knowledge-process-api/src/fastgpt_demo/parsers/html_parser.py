"""HTML parser — 使用 BeautifulSoup 提取文本和结构化内容。"""

from __future__ import annotations

import chardet
from bs4 import BeautifulSoup

from ._types import ParseResult

NOISE_TAGS = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']
CONTENT_SELECTORS = ['article', 'main', 'div.content', 'div.article', 'div#content']


def parse(buffer: bytes, remove_noise: bool = True, **kwargs) -> ParseResult:
    """解析 HTML 文件，提取纯文本和结构化 HTML 预览。

    - raw_text: 原始 HTML 内容（供 Markdown 转换器使用，始终保留完整 HTML）
    - format_text: 清洗后的 HTML（移除干扰标签、识别主要内容区域）
    - html_preview: 结构化 HTML 预览
    """

    try:
        html_str = buffer.decode("utf-8")
    except UnicodeDecodeError:
        detection = chardet.detect(buffer)
        fallback_encoding: str = detection.get("encoding") or "utf-8"
        html_str = buffer.decode(fallback_encoding, errors="replace")

    soup = BeautifulSoup(html_str, "html.parser")

    raw_text = str(soup)

    if remove_noise:
        for tag in soup.find_all(NOISE_TAGS):
            tag.decompose()

        main_content = None
        for selector in CONTENT_SELECTORS:
            main_content = soup.select_one(selector)
            if main_content:
                break

        content_soup = main_content if main_content else (soup.body if soup.body else soup)
    else:
        content_soup = soup.body if soup.body else soup

    format_text = str(content_soup)
    html_preview = str(content_soup)

    return ParseResult(
        raw_text=raw_text,
        format_text=format_text,
        html_preview=html_preview,
        image_list=[],
    )
