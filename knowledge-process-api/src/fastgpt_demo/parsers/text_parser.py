"""TXT / MD parser — encoding detection via chardet."""

from __future__ import annotations

import chardet

from ._types import ParseResult


def parse(buffer: bytes, **kwargs) -> ParseResult:
    """Parse a plain-text buffer with automatic encoding detection."""

    detection = chardet.detect(buffer)
    encoding: str = detection.get("encoding") or "utf-8"
    confidence: float = detection.get("confidence", 0.0)

    if confidence < 0.7:
        encoding = "utf-8"

    raw_text = buffer.decode(encoding, errors="replace")

    return ParseResult(
        raw_text=raw_text,
        format_text=raw_text,
        html_preview=f"<pre>{raw_text}</pre>",
        image_list=[],
    )
