"""Marker document parser — converts PDF/image/Office files to markdown/JSON/HTML."""

from __future__ import annotations

import os
import tempfile
from pathlib import PurePosixPath

from ._types import ParseResult

# Marker supported file extensions
SUPPORTED_MARKER_EXTS = {
    ".pdf",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
    ".docx", ".doc",
    ".pptx", ".ppt",
    ".xlsx", ".xls",
    ".html", ".htm",
    ".epub",
}

DEFAULT_OUTPUT_FORMAT = "markdown"


def parse(buffer: bytes, filename: str) -> ParseResult:
    """Parse document using Marker engine.

    Marker converts documents to markdown, JSON, chunks, and HTML quickly and accurately.
    Supports PDF, images, PPTX, DOCX, XLSX, HTML, EPUB files in all languages.
    """
    ext = PurePosixPath(filename).suffix.lower()
    if ext not in SUPPORTED_MARKER_EXTS:
        raise ValueError(
            f"Marker does not support {ext} files. "
            f"Supported: {', '.join(sorted(SUPPORTED_MARKER_EXTS))}"
        )

    return _call_marker(buffer, filename)


def _call_marker(buffer: bytes, filename: str) -> ParseResult:
    """Call Marker PDF converter."""
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        # Write buffer to a temporary file for marker to process
        with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp:
            tmp.write(buffer)
            tmp_path = tmp.name

        try:
            # Create converter with default model dict
            converter = PdfConverter(
                artifact_dict=create_model_dict(),
            )

            # Convert the file
            rendered = converter(tmp_path)

            # Extract text, metadata, and images
            text, _, images = text_from_rendered(rendered)

            # rendered.markdown contains the full markdown output
            raw_text = rendered.markdown if hasattr(rendered, 'markdown') else text
            html_preview = _build_html_preview(filename, raw_text)

            return ParseResult(
                raw_text=raw_text,
                format_text=raw_text,
                html_preview=html_preview,
                image_list=[],
                sheet_names=None,
            )

        finally:
            # Clean up temp file
            os.unlink(tmp_path)

    except ImportError as e:
        return _error_result(
            filename,
            "Marker 未安装",
            f"请运行: pip install marker-pdf\n错误: {str(e)}"
        )
    except Exception as e:
        return _error_result(filename, f"Marker 解析失败: {str(e)}", str(e))


def _build_html_preview(filename: str, md_content: str) -> str:
    """Build HTML preview showing Marker markdown content."""
    sections = []

    sections.append(f'''
    <div class="marker-preview">
      <div class="marker-header">
        <span class="marker-badge">Marker</span>
        <span class="marker-file">{filename}</span>
      </div>
      <div class="marker-content">
    ''')

    if md_content:
        sections.append(_escape_html(md_content))
    else:
        sections.append(f'''
        <div class="marker-no-data">Marker 未返回内容</div>
        ''')

    sections.append('</div></div>')

    sections.append('''
    <style>
      .marker-preview {
        padding: 12px;
        background: rgba(168, 85, 247, 0.04);
        border-radius: 8px;
        border: 1px solid rgba(168, 85, 247, 0.15);
      }
      .marker-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(168, 85, 247, 0.2);
      }
      .marker-badge {
        background: #a855f7;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
      }
      .marker-file {
        font-size: 0.82rem;
        color: #64748b;
      }
      .marker-content {
        font-size: 0.82rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
        padding: 10px;
        border-radius: 6px;
        overflow-y: auto;
        max-height: 500px;
      }
      .marker-no-data {
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


def _error_result(filename: str, error_title: str, error_detail: str) -> ParseResult:
    """Build error ParseResult."""
    raw = f"[Marker Error] {error_title}\n\n文件: {filename}\n{error_detail}"
    html = f'''
    <div style="padding:16px;background:rgba(239,68,68,0.06);border-radius:8px;border:1px solid rgba(239,68,68,0.2)">
      <div style="font-size:0.9rem;font-weight:600;color:#ef4444;margin-bottom:8px">{error_title}</div>
      <div style="font-size:0.82rem;color:#64748b;line-height:1.7">
        <p>文件: <code>{filename}</code></p>
        <p>解析引擎: Marker</p>
        {f'<p>详情: {error_detail}</p>' if error_detail else ''}
      </div>
    </div>
    '''
    return ParseResult(
        raw_text=raw,
        format_text=raw,
        html_preview=html,
        image_list=[],
        sheet_names=None,
    )
