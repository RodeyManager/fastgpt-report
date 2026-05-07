"""Document parsers for FastGPT demo — routes by file extension and engine."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Callable

from ._types import ParseResult
from .csv_parser import parse as parse_csv
from .docx_parser import parse as parse_docx
from .docling_parser import parse as parse_docling, SUPPORTED_DOCLING_EXTS
from .marker_parser import parse as parse_marker, SUPPORTED_MARKER_EXTS
from .mineru_parser import parse as parse_mineru, SUPPORTED_MINERU_EXTS
from .mineru_saas_parser import parse as parse_mineru_saas, SUPPORTED_SAAS_EXTS
from .mineru_precision_parser import parse as parse_mineru_precision, SUPPORTED_PRECISION_EXTS
from .pdf_parser import parse as parse_pdf
from .pptx_parser import parse as parse_pptx
from .html_parser import parse as parse_html
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
    ".html": "html",
    ".htm": "html",
}


def parse_file(
    buffer: bytes,
    filename: str,
    method: str = "auto",
    engine: str = "fastgpt",
    header_footer_ratio: float = 0.05,
    remove_html_noise: bool = True,
) -> ParseResult:
    """Dispatch *buffer* to the correct parser based on *engine* and *filename* extension.

    Args:
        header_footer_ratio: Fraction of page height to filter as header/footer
            (PDF only). Default 0.05 (5%). Set to 0 to disable.
    """

    ext = PurePosixPath(filename).suffix.lower()

    if engine == "mineru":
        if ext not in SUPPORTED_MINERU_EXTS:
            raise ValueError(
                f"MinerU does not support {ext} files. "
                f"Supported: {', '.join(sorted(SUPPORTED_MINERU_EXTS))}"
            )
        return parse_mineru(buffer, filename)

    if engine == "mineru_saas":
        if ext not in SUPPORTED_SAAS_EXTS:
            raise ValueError(
                f"MinerU SaaS does not support {ext} files. "
                f"Supported: {', '.join(sorted(SUPPORTED_SAAS_EXTS))}"
            )
        return parse_mineru_saas(buffer, filename)

    if engine == "mineru_precision":
        if ext not in SUPPORTED_PRECISION_EXTS:
            raise ValueError(
                f"MinerU Precision API does not support {ext} files. "
                f"Supported: {', '.join(sorted(SUPPORTED_PRECISION_EXTS))}"
            )
        return parse_mineru_precision(buffer, filename)

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

    if engine == "docling":
        if ext not in SUPPORTED_DOCLING_EXTS:
            raise ValueError(
                f"Docling does not support {ext} files. "
                f"Supported: {', '.join(sorted(SUPPORTED_DOCLING_EXTS))}"
            )
        return parse_docling(buffer, filename)

    if engine == "opendataloader-pdf":
        if ext != ".pdf":
            raise ValueError(
                f"opendataloader-pdf 引擎仅支持 PDF 文件，"
                f"当前文件类型: {ext}"
            )
        from .opendataloader_pdf_parser import parse_opendataloader_pdf

        return parse_opendataloader_pdf(buffer)

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
        "html": parse_html,
    }

    handler = dispatch.get(parser_key)
    if handler is None:
        raise ValueError(f"Unknown parse method: {parser_key}")

    if parser_key == "pdf":
        return handler(buffer, header_footer_ratio=header_footer_ratio)

    if parser_key == "html":
        return handler(buffer, remove_noise=remove_html_noise)

    return handler(buffer)


__all__ = ["ParseResult", "parse_file"]
