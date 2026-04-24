"""DOCX parser — uses mammoth for HTML and raw-text extraction."""

from __future__ import annotations

from io import BytesIO

import mammoth

from ._types import ParseResult


def parse(buffer: bytes, **kwargs) -> ParseResult:
    """Parse a DOCX buffer returning both raw text and HTML preview."""

    file_obj = BytesIO(buffer)

    html_result = mammoth.convert_to_html(file_obj, ignore_empty_paragraphs=False)
    html_preview: str = html_result.value

    file_obj.seek(0)

    text_result = mammoth.extract_raw_text(file_obj)
    raw_text: str = text_result.value

    return ParseResult(
        raw_text=raw_text,
        format_text=raw_text,
        html_preview=html_preview,
        image_list=[],
    )
