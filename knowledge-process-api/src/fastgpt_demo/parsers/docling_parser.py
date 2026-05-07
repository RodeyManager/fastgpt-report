"""Docling parser for FastGPT demo — supports multiple document formats."""

from __future__ import annotations

import tempfile
from pathlib import Path

from docling.datamodel.base_models import ConversionStatus
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter

from ._types import ParseResult


SUPPORTED_DOCLING_EXTS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".csv",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
}


def parse(buffer: bytes, filename: str) -> ParseResult:
    """Parse a document using Docling and return structured results.

    Returns both Markdown (format_text) and HTML (html_preview) representations.
    """
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_DOCLING_EXTS:
        raise ValueError(
            f"Docling does not support {ext} files. "
            f"Supported: {', '.join(sorted(SUPPORTED_DOCLING_EXTS))}"
        )

    # Write buffer to a temporary file — Docling works best with file paths
    suffix = ext if ext else ".tmp"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(buffer)
        tmp_path = Path(tmp_file.name)

    try:
        converter = DocumentConverter()
        result: ConversionResult = converter.convert(str(tmp_path))

        if result.status != ConversionStatus.SUCCESS:
            raise RuntimeError(f"Docling conversion failed: {result.status}")

        doc = result.document

        # Export to different formats
        markdown_text = doc.export_to_markdown()
        html_text = doc.export_to_html()
        raw_text = doc.export_to_text()

        # Extract images if any
        image_list = []
        for pic in doc.pictures:
            if pic.image and pic.image.data:
                image_list.append({
                    "mime_type": pic.image.mime_type or "image/png",
                    "size": len(pic.image.data),
                })

        # Build HTML preview with Docling styling (consistent with MinerU format)
        html_preview = _build_html_preview(filename, markdown_text, html_text)

        return ParseResult(
            raw_text=raw_text,
            format_text=markdown_text,
            html_preview=html_preview,
            image_list=image_list,
        )
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()


def _build_html_preview(filename: str, md_content: str, html_content: str) -> str:
    """Build HTML preview showing Docling content with consistent styling."""
    sections = []

    # Header
    sections.append(f'''
    <div class="docling-preview">
      <div class="docling-header">
        <span class="docling-badge">Docling</span>
        <span class="docling-file">{filename}</span>
      </div>
      <div class="docling-content">
    ''')

    # Show markdown content (consistent with MinerU display)
    if md_content:
        sections.append(_escape_html(md_content))
    else:
        sections.append(f'''
        <div class="docling-no-data">Docling 未返回 Markdown 内容</div>
        ''')

    sections.append('</div></div>')

    # Add styles (consistent with MinerU styling)
    sections.append('''
    <style>
      .docling-preview {
        padding: 12px;
        background: rgba(99, 102, 241, 0.04);
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.15);
      }
      .docling-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
      }
      .docling-badge {
        background: #6366f1;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
      }
      .docling-file {
        font-size: 0.82rem;
        color: #64748b;
      }
      .docling-content {
        font-size: 0.82rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
        padding: 10px;
        border-radius: 6px;
        overflow-y: auto;
      }
      .docling-no-data {
        font-size: 0.82rem;
        color: #94a3b8;
        padding: 10px;
        text-align: center;
      }
    </style>
    ''')

    return "\n".join(sections)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))
