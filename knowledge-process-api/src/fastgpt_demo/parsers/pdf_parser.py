"""PDF parser — page-by-page text extraction with Y-position filtering."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pymupdf

from ._types import ParseResult

_SENTENCE_ENDS = (".", "。", "！", "!", "?", "？", ";", "；")


def _extract_page_text(page: pymupdf.Page, header_footer_ratio: float = 0.05) -> str:
    """Extract text from a single PDF page, filtering header/footer regions.

    Args:
        page: A PyMuPDF page object.
        header_footer_ratio: Fraction of page height to treat as header (top)
            and footer (bottom). Default 0.05 means top 5% and bottom 5%.
            Set to 0 to disable header/footer filtering.
    """

    page_height: float = page.rect.height
    top_threshold = page_height * header_footer_ratio
    bottom_threshold = page_height * (1 - header_footer_ratio)

    blocks: list[dict[str, Any]] = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)["blocks"]

    page_lines: list[str] = []

    for block in blocks:
        if block.get("type") != 0:  # skip image blocks
            continue

        for line in block.get("lines", []):
            line_text_parts: list[str] = []

            for span in line.get("spans", []):
                bbox = span.get("bbox")
                if bbox is None:
                    continue

                y_bottom: float = bbox[3]

                # Skip spans in top 5% or bottom 5% (headers / footers)
                if y_bottom < top_threshold or y_bottom > bottom_threshold:
                    continue

                span_text: str = span.get("text", "")
                if span_text:
                    line_text_parts.append(span_text)

            if line_text_parts:
                line_text = "".join(line_text_parts)
                page_lines.append(line_text)

    # Join lines with newline, adding extra newline after sentence-ending punctuation
    result_parts: list[str] = []
    for line in page_lines:
        result_parts.append(line)
        if line.rstrip().endswith(_SENTENCE_ENDS):
            result_parts.append("\n")

    return "\n".join(result_parts)


def parse(buffer: bytes, header_footer_ratio: float = 0.05, **kwargs) -> ParseResult:
    """Parse a PDF buffer and return structured text.

    Args:
        buffer: PDF file content as bytes.
        header_footer_ratio: Fraction of page height to filter as header/footer.
            Default 0.05 (5%). Set to 0 to disable filtering.
    """

    doc: pymupdf.Document = pymupdf.open(stream=buffer, filetype="pdf")

    pages_text: list[str] = []
    for page in doc:
        pages_text.append(_extract_page_text(page, header_footer_ratio))

    raw_text = "\n".join(pages_text)
    doc.close()

    return ParseResult(
        raw_text=raw_text,
        format_text=raw_text,
        html_preview=f"<pre>{raw_text}</pre>",
        image_list=[],
    )
