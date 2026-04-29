"""Document parsers for FastGPT demo — routes by file extension and engine."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Callable

from ._types import ParseResult
from .csv_parser import parse as parse_csv
from .docx_parser import parse as parse_docx
from .marker_parser import parse as parse_marker, SUPPORTED_MARKER_EXTS
from .mineru_parser import parse as parse_mineru, SUPPORTED_MINERU_EXTS
from .pdf_parser import parse as parse_pdf
from .pptx_parser import parse as parse_pptx
from .text_parser import parse as parse_text
from .unstructured_parser import parse as parse_unstructured, SUPPORTED_UNSTRUCTURED_EXTS  # noqa: E402
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
    engine: str = "fastgpt",
) -> ParseResult:
    """Dispatch *buffer* to the correct parser based on *engine* and *filename* extension."""

    ext = PurePosixPath(filename).suffix.lower()

    if engine == "mineru":
        if ext not in SUPPORTED_MINERU_EXTS:
            raise ValueError(
                f"MinerU does not support {ext} files. "
                f"Supported: {', '.join(sorted(SUPPORTED_MINERU_EXTS))}"
            )
        return parse_mineru(buffer, filename)

    if engine == "unstructured":
        if ext not in SUPPORTED_UNSTRUCTURED_EXTS:
            raise ValueError(
                f"Unstructured-API does not support {ext} files. "
                f"Supported: {', '.join(sorted(SUPPORTED_UNSTRUCTURED_EXTS))}"
            )
        return parse_unstructured(buffer, filename)

    if engine == "marker":
        if ext not in SUPPORTED_MARKER_EXTS:
            raise ValueError(
                f"Marker does not support {ext} files. "
                f"Supported: {', '.join(sorted(SUPPORTED_MARKER_EXTS))}"
            )
        return parse_marker(buffer, filename)

    # fastgpt (default) — existing logic unchanged
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
