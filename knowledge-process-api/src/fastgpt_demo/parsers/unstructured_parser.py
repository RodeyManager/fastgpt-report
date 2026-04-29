"""Unstructured-API document parser — calls local Unstructured-API service."""

from __future__ import annotations

import os
from pathlib import PurePosixPath

import requests

from ._types import ParseResult

# Unstructured-API supported file extensions
SUPPORTED_UNSTRUCTURED_EXTS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".csv", ".xlsx", ".xls",
    ".txt", ".md", ".markdown",
    ".html", ".htm"
}

# Default API endpoint
DEFAULT_API_URL = "http://localhost:9500/general/v0/general"
DEFAULT_STRATEGY = "hi_res"


def parse(buffer: bytes, filename: str, api_url: str | None = None, strategy: str = DEFAULT_STRATEGY) -> ParseResult:
    """Parse document using Unstructured-API.

    Args:
        buffer: File content as bytes
        filename: Original filename
        api_url: Unstructured-API endpoint (default: http://localhost:9500/general/v0/general)
        strategy: Parsing strategy (default: hi_res)

    Returns:
        ParseResult with extracted text and HTML preview
    """
    ext = PurePosixPath(filename).suffix.lower()
    if ext not in SUPPORTED_UNSTRUCTURED_EXTS:
        raise ValueError(
            f"Unstructured-API does not support {ext} files. "
            f"Supported: {', '.join(sorted(SUPPORTED_UNSTRUCTURED_EXTS))}"
        )

    api_url = api_url or os.environ.get("UNSTRUCTURED_API_URL", DEFAULT_API_URL)

    return _call_unstructured_api(buffer, filename, api_url, strategy)


def _call_unstructured_api(
    buffer: bytes,
    filename: str,
    api_url: str,
    strategy: str
) -> ParseResult:
    """Call Unstructured-API service."""
    try:
        # Build mime type map
        file_ext = PurePosixPath(filename).suffix.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".ppt": "application/vnd.ms-powerpoint",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".csv": "text/csv",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".html": "text/html",
            ".htm": "text/html",
        }
        mime_type = mime_types.get(file_ext, "application/octet-stream")

        response = requests.post(
            api_url,
            files={"files": (filename, buffer, mime_type)},
            data={"strategy": strategy},
            timeout=120
        )

        if response.status_code != 200:
            return _error_result(filename, f"Unstructured-API error: HTTP {response.status_code}", response.text)

        result = response.json()

        # Parse the response - Unstructured-API returns array of elements
        elements = result if isinstance(result, list) else result.get("elements", [])
        if not isinstance(elements, list):
            elements = [elements]

        # Handle empty result
        if not elements or (isinstance(elements, list) and len(elements) == 0):
            return _error_result(filename, "未提取到文本内容", "API 返回空结果 - 文件可能为空或无法解析")

        # Extract text from elements
        raw_text_parts = []
        html_parts = []

        for element in elements:
            text = element.get("text", "")
            element_type = element.get("type", "Text")

            if text and text.strip():
                raw_text_parts.append(text.strip())

                # Build HTML with type label
                if element_type == "Title":
                    html_parts.append(f'<div class="unstructured-element title">{text}</div>')
                elif element_type == "NarrativeText":
                    html_parts.append(f'<div class="unstructured-element narrative">{text}</div>')
                elif element_type == "Table":
                    # Table content as pre-formatted text
                    html_parts.append(f'<div class="unstructured-element table"><pre>{text}</pre></div>')
                elif element_type == "Image":
                    html_parts.append(f'<div class="unstructured-element image">{text}</div>')
                else:
                    html_parts.append(f'<div class="unstructured-element">{text}</div>')

        raw_text = "\n\n".join(raw_text_parts)
        html_preview = _build_html_preview(filename, html_parts, len(elements))

        return ParseResult(
            raw_text=raw_text,
            format_text=raw_text,
            html_preview=html_preview,
            image_list=[],
            sheet_names=None,
        )

    except requests.exceptions.ConnectionError:
        return _error_result(
            filename,
            "无法连接到 Unstructured-API 服务",
            f"请确保 Unstructured-API 服务正在运行于 {api_url}"
        )
    except requests.exceptions.Timeout:
        return _error_result(filename, "Unstructured-API 请求超时", "文件可能太大或服务响应慢")
    except Exception as e:
        return _error_result(filename, f"Unstructured-API 解析失败: {str(e)}", str(e))


def _build_html_preview(filename: str, html_parts: list[str], element_count: int) -> str:
    """Build HTML preview from parsed elements."""
    if not html_parts:
        return _error_html(filename, "未提取到文本内容", "")

    content = "\n".join(html_parts)

    return f'''<div class="unstructured-preview">
  <div class="unstructured-header">
    <span class="unstructured-badge">Unstructured-API</span>
    <span class="unstructured-file">{filename}</span>
    <span class="unstructured-count">{element_count} 元素</span>
  </div>
  <div class="unstructured-content">
    {content}
  </div>
  <style>
    .unstructured-preview {{
      padding: 12px;
      background: rgba(34, 197, 94, 0.04);
      border-radius: 8px;
      border: 1px solid rgba(34, 197, 94, 0.15);
    }}
    .unstructured-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid rgba(34, 197, 94, 0.2);
    }}
    .unstructured-badge {{
      background: #22c55e;
      color: white;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
    }}
    .unstructured-file {{
      font-size: 0.82rem;
      color: var(--text-secondary);
    }}
    .unstructured-count {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-left: auto;
    }}
    .unstructured-content {{
      font-size: 0.85rem;
      line-height: 1.7;
    }}
    .unstructured-element {{
      margin-bottom: 8px;
    }}
    .unstructured-element.title {{
      font-size: 1.1rem;
      font-weight: 700;
      color: #1a1a2e;
      margin-top: 16px;
      margin-bottom: 12px;
    }}
    .unstructured-element.narrative {{
      color: #334155;
    }}
    .unstructured-element.table {{
      background: rgba(99, 102, 241, 0.05);
      padding: 12px;
      border-radius: 6px;
      overflow-x: auto;
    }}
    .unstructured-element.table pre {{
      margin: 0;
      font-family: inherit;
      white-space: pre-wrap;
    }}
  </style>
</div>'''


def _error_html(filename: str, error_title: str, error_detail: str) -> str:
    """Build error HTML preview."""
    return f'''<div style="padding:16px;background:rgba(239,68,68,0.06);border-radius:8px;border:1px solid rgba(239,68,68,0.2)">
  <div style="font-size:0.9rem;font-weight:600;color:#ef4444;margin-bottom:8px">{error_title}</div>
  <div style="font-size:0.82rem;color:#64748b;line-height:1.7">
    <p>文件: <code>{filename}</code></p>
    <p>解析引擎: Unstructured-API</p>
    {f'<p>详情: {error_detail}</p>' if error_detail else ''}
  </div>
</div>'''


def _error_result(filename: str, error_title: str, error_detail: str) -> ParseResult:
    """Build error ParseResult."""
    raw = f"[Unstructured-API Error] {error_title}\n\n文件: {filename}\n{error_detail}"
    html = _error_html(filename, error_title, error_detail)
    return ParseResult(
        raw_text=raw,
        format_text=raw,
        html_preview=html,
        image_list=[],
        sheet_names=None,
    )