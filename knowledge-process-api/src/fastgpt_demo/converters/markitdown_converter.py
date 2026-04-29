"""Markitdown-based HTML-to-Markdown converter module."""

from __future__ import annotations

from io import BytesIO

from markitdown import MarkItDown

from .markdown_converter import simple_markdown_text


def html_to_markdown_markitdown(html: str) -> str:
    """Convert HTML string to Markdown using Microsoft's markitdown library.

    Wraps the HTML in a BytesIO stream and passes it to markitdown's
    convert_stream() with file_extension=".html".
    """
    if not html or not html.strip():
        return ""

    md_converter = MarkItDown()
    stream = BytesIO(html.encode("utf-8"))
    result = md_converter.convert_stream(stream, file_extension=".html")
    raw_md = result.text_content or ""

    return simple_markdown_text(raw_md)
