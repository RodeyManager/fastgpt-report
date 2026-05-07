"""MinerU document parser — calls local MinerU Docker service."""

from __future__ import annotations

import os
from pathlib import PurePosixPath

import requests

from ._types import ParseResult

# MinerU supported file extensions
SUPPORTED_MINERU_EXTS = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".png", ".jpg", ".jpeg", ".gif", ".webp"}

# Default API endpoint for local Docker deployment
DEFAULT_API_URL = "http://127.0.0.1:8000/file_parse"


def parse(buffer: bytes, filename: str) -> ParseResult:
    """Parse document using MinerU engine.

    If MINERU_API_URL is set, calls the local MinerU API.
    Otherwise returns placeholder data for testing.
    """
    ext = PurePosixPath(filename).suffix.lower()
    if ext not in SUPPORTED_MINERU_EXTS:
        raise ValueError(
            f"MinerU does not support {ext} files. "
            f"Supported: {', '.join(sorted(SUPPORTED_MINERU_EXTS))}"
        )

    api_url = os.environ.get("MINERU_API_URL", DEFAULT_API_URL)

    return _call_mineru_api(buffer, filename, api_url)


def _call_mineru_api(buffer: bytes, filename: str, api_url: str) -> ParseResult:
    """Call local MinerU Docker API service (CPU pipeline mode)."""
    
    try:
        # Send file to MinerU API - CPU mode with pipeline backend
        # 使用同步模式，直接等待结果返回，不轮询
        response = requests.post(
            api_url,
            files={"files": (filename, buffer)},
            data={
                "lang_list": "ch",
                "backend": "pipeline",    # CPU pipeline mode
                "parse_method": "auto",   # Auto detect
                "formula_enable": "false",
                "server_url":"string",
                "table_enable":"true",
                "return_md": "true",
                "return_middle_json":"false",
                "return_model_output":"false",
                "return_content_list":"false",
                "return_images":"false",
                "response_format_zip": "false",
                "return_original_file": "false",
                "start_page_id": "0",
                "end_page_id":"99999"
            },
            timeout=600  # 10 minutes timeout for synchronous processing
        )

        if response.status_code == 409:
            # Task failed immediately
            error_data = response.json()
            error_msg = error_data.get("error", error_data.get("message", "Unknown error"))
            return _error_result(filename, "MinerU 任务失败", error_msg)

        if response.status_code != 200:
            return _error_result(filename, f"MinerU API error: HTTP {response.status_code}", response.text[:500])

        result = response.json()
        
        # Direct result (sync) - MinerU should return result directly when using synchronous mode
        return _parse_mineru_response(result, filename)

    except requests.exceptions.ConnectionError:
        return _error_result(
            filename,
            "无法连接到 MinerU 服务",
            f"请确保 MinerU Docker 服务正在运行于 {api_url}"
        )
    except requests.exceptions.Timeout:
        return _error_result(filename, "MinerU 请求超时", "文件可能太大或服务响应慢")
    except Exception as e:
        return _error_result(filename, f"MinerU 解析失败: {str(e)}", str(e))


def _parse_mineru_response(result: dict, filename: str) -> ParseResult:
    """Parse MinerU API response and extract all data types."""
    
    # MinerU Docker API returns nested results: { "results": { "filename": { "md_content": "...", ... } } }
    md_content = ""
    nested_results = result.get("results", {})
    if isinstance(nested_results, dict) and nested_results:
        # Get the first (and usually only) file result
        first_file_result = next(iter(nested_results.values()), {})
        if isinstance(first_file_result, dict):
            md_content = first_file_result.get("md_content", "")

    # If still empty, include full JSON
    if not md_content:
        md_content = str(result)

    raw_text = md_content
    html_preview = _build_html_preview(filename, md_content)

    return ParseResult(
        raw_text=raw_text,
        format_text=raw_text,
        html_preview=html_preview,
        image_list=[],
        sheet_names=None,
        results=None,
    )


def _build_html_preview(filename: str, md_content: str) -> str:
    """Build HTML preview showing MinerU Markdown content."""
    sections = []

    # Header
    sections.append(f'''
    <div class="mineru-preview">
      <div class="mineru-header">
        <span class="mineru-badge">MinerU</span>
        <span class="mineru-file">{filename}</span>
      </div>
      <div class="mineru-content">
    ''')

    # Show markdown content
    if md_content:
        sections.append(_escape_html(md_content))
    else:
        sections.append(f'''
        <div class="mineru-no-data">MinerU 未返回 Markdown 内容</div>
        ''')

    sections.append('</div></div>')

    # Add styles
    sections.append('''
    <style>
      .mineru-preview {
        padding: 12px;
        background: rgba(99, 102, 241, 0.04);
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.15);
      }
      .mineru-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
      }
      .mineru-badge {
        background: #6366f1;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
      }
      .mineru-file {
        font-size: 0.82rem;
        color: #64748b;
      }
      .mineru-content {
        font-size: 0.82rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
        padding: 10px;
        border-radius: 6px;
        overflow-y: auto;
      }
      .mineru-no-data {
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
    raw = f"[MinerU Error] {error_title}\n\n文件: {filename}\n{error_detail}"
    html = f'''
    <div style="padding:16px;background:rgba(239,68,68,0.06);border-radius:8px;border:1px solid rgba(239,68,68,0.2)">
      <div style="font-size:0.9rem;font-weight:600;color:#ef4444;margin-bottom:8px">{error_title}</div>
      <div style="font-size:0.82rem;color:#64748b;line-height:1.7">
        <p>文件: <code>{filename}</code></p>
        <p>解析引擎: MinerU</p>
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
