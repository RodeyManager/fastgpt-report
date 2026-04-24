"""Document parsers for FastGPT demo — routes by file extension."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Callable

from ._types import ParseResult
from .csv_parser import parse as parse_csv
from .docx_parser import parse as parse_docx
from .pdf_parser import parse as parse_pdf
from .pptx_parser import parse as parse_pptx
from .text_parser import parse as parse_text
from .xlsx_parser import parse as parse_xlsx


_EXTENSION_MAP: dict[str, str] = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".pptx": "pptx",
    ".txt": "text",
    ".md": "text",
    ".markdown": "text",
}


def parse_file(
    buffer: bytes,
    filename: str,
    method: str = "auto",
) -> ParseResult:
    """Dispatch *buffer* to the correct parser based on *filename* extension."""

    ext = PurePosixPath(filename).suffix.lower()

    if method == "auto":
        parser_key = _EXTENSION_MAP.get(ext)
        if parser_key is None:
            raise ValueError(f"Unsupported file extension: {ext}")
    else:
        parser_key = method

    dispatch: dict[str, Callable] = {
        "pdf": parse_pdf,
        "docx": parse_docx,
        "csv": parse_csv,
        "xlsx": parse_xlsx,
        "pptx": parse_pptx,
        "text": parse_text,
    }

    handler = dispatch.get(parser_key)
    if handler is None:
        raise ValueError(f"Unknown parse method: {parser_key}")

    return handler(buffer)


__all__ = ["ParseResult", "parse_file"]
