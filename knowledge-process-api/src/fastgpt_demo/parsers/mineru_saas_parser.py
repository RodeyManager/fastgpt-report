"""MinerU SaaS API parser — calls official MinerU cloud service.

Uses the Agent lightweight API (免登录) for quick parsing.
Ref: https://mineru.net/apiManage/docs

Two modes:
- URL mode: submit remote URL, poll for result
- File mode: get signed upload URL, upload file, poll for result
"""

from __future__ import annotations

import time
from pathlib import PurePosixPath

import requests

from ._types import ParseResult

# MinerU SaaS API endpoints (Agent lightweight API)
MINERU_SAAS_BASE = "https://mineru.net/api/v1/agent"
SUBMIT_URL_ENDPOINT = f"{MINERU_SAAS_BASE}/parse/url"
SUBMIT_FILE_ENDPOINT = f"{MINERU_SAAS_BASE}/parse/file"
QUERY_ENDPOINT = f"{MINERU_SAAS_BASE}/parse"

# Supported file extensions for SaaS API
SUPPORTED_SAAS_EXTS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".jp2", ".webp", ".gif", ".bmp",
    ".docx", ".pptx", ".xlsx"
}

# Polling config
POLL_INTERVAL = 3  # seconds
POLL_TIMEOUT = 300  # 5 minutes


def parse(buffer: bytes, filename: str) -> ParseResult:
    """Parse document using MinerU SaaS API.

    Args:
        buffer: File content bytes
        filename: Original filename (used to determine file type)

    Returns:
        ParseResult with extracted text and HTML preview
    """
    ext = PurePosixPath(filename).suffix.lower()
    if ext not in SUPPORTED_SAAS_EXTS:
        raise ValueError(
            f"MinerU SaaS does not support {ext} files. "
            f"Supported: {', '.join(sorted(SUPPORTED_SAAS_EXTS))}"
        )

    # Use file upload mode (signing URL)
    return _parse_via_upload(buffer, filename)


def _parse_via_upload(buffer: bytes, filename: str) -> ParseResult:
    """Upload file to MinerU SaaS and poll for result."""
    try:
        # Step 1: Get signed upload URL
        file_payload = {
            "file_name": filename,
            "language": "ch",
            "enable_table": True,
            "is_ocr": False,
            "enable_formula": True,
        }

        resp = requests.post(SUBMIT_FILE_ENDPOINT, json=file_payload, timeout=30)
        if resp.status_code == 429:
            return _error_result(
                filename,
                "MinerU SaaS 请求过于频繁",
                "IP 限频，请稍后再试或使用标准 API"
            )

        result = resp.json()
        if result.get("code") != 0:
            return _error_result(
                filename,
                f"MinerU SaaS 错误 (code={result.get('code')})",
                result.get("msg", "未知错误")
            )

        task_id = result["data"]["task_id"]
        file_url = result["data"]["file_url"]

        # Step 2: Upload file to signed URL
        upload_resp = requests.put(file_url, data=buffer, timeout=120)
        if upload_resp.status_code not in (200, 201):
            return _error_result(
                filename,
                "文件上传失败",
                f"HTTP {upload_resp.status_code}: {upload_resp.text[:200] if upload_resp.text else 'empty'}"
            )

        # Step 3: Poll for result
        return _poll_result(filename, task_id)

    except requests.exceptions.ConnectionError:
        return _error_result(
            filename,
            "无法连接到 MinerU SaaS",
            "请检查网络连接或稍后重试"
        )
    except requests.exceptions.Timeout:
        return _error_result(filename, "请求超时", "文件可能太大或服务响应慢")
    except Exception as e:
        return _error_result(filename, f"MinerU SaaS 解析失败: {str(e)}", str(e))


def _poll_result(filename: str, task_id: str) -> ParseResult:
    """Poll MinerU SaaS until task completes or times out."""
    state_labels = {
        "uploading": "文件下载中",
        "pending": "排队中",
        "running": "解析中",
        "waiting-file": "等待文件上传",
    }

    start_time = time.time()

    while time.time() - start_time < POLL_TIMEOUT:
        try:
            resp = requests.get(f"{QUERY_ENDPOINT}/{task_id}", timeout=30)
            result = resp.json()

            if result.get("code") != 0:
                return _error_result(
                    filename,
                    f"查询失败 (code={result.get('code')})",
                    result.get("msg", "未知错误")
                )

            state = result["data"]["state"]
            elapsed = int(time.time() - start_time)

            if state == "done":
                markdown_url = result["data"]["markdown_url"]
                print(f'data: {result["data"]}')
                # Download markdown content
                md_content = _download_markdown(markdown_url)
                return _build_result(filename, md_content)

            if state == "failed":
                err_msg = result["data"].get("err_msg", "未知错误")
                err_code = result["data"].get("err_code", "N/A")
                return _error_result(
                    filename,
                    f"MinerU SaaS 解析失败 (err_code={err_code})",
                    err_msg
                )

            # Still processing, continue polling
            label = state_labels.get(state, state)
            # Note: We don't have a callback here, so we just wait

        except requests.exceptions.RequestException as e:
            return _error_result(filename, "轮询请求失败", str(e))

    return _error_result(
        filename,
        "轮询超时",
        f"等待 {POLL_TIMEOUT} 秒后未获取结果，请稍后手动查询 task_id: {task_id}"
    )


def _download_markdown(url: str) -> str:
    """Download markdown content from CDN URL with proper encoding handling."""
    try:
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200:
            # Try multiple encodings commonly used for Chinese content
            for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']:
                try:
                    return resp.content.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    continue
            # Fall back to latin-1 which always succeeds
            return resp.content.decode('latin-1')
        return f"[Error: 无法下载 Markdown，HTTP {resp.status_code}]"
    except Exception as e:
        return f"[Error: 下载 Markdown 失败: {str(e)}]"


def _build_result(filename: str, md_content: str) -> ParseResult:
    """Build successful ParseResult."""
    # Check for empty or very short content
    if not md_content or len(md_content.strip()) < 10:
        return _error_result(
            filename,
            "MinerU SaaS 返回内容为空",
            "文件可能无法解析或内容为空，请尝试其他文件"
        )

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
    """Build HTML preview showing MinerU SaaS Markdown content."""
    sections = []

    # Header
    sections.append(f'''
    <div class="mineru-saas-preview">
      <div class="mineru-saas-header">
        <span class="mineru-saas-badge">MinerU SaaS</span>
        <span class="mineru-saas-file">{filename}</span>
      </div>
      <div class="mineru-saas-content">
    ''')

    # Show markdown content
    if md_content:
        sections.append(_escape_html(md_content))
    else:
        sections.append(f'''
        <div class="mineru-saas-no-data">MinerU SaaS 未返回 Markdown 内容</div>
        ''')

    sections.append('</div></div>')

    # Add styles
    sections.append('''
    <style>
      .mineru-saas-preview {
        padding: 12px;
        background: rgba(99, 102, 241, 0.04);
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.15);
      }
      .mineru-saas-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
      }
      .mineru-saas-badge {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
      }
      .mineru-saas-file {
        font-size: 0.82rem;
        color: #64748b;
      }
      .mineru-saas-content {
        font-size: 0.82rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
        padding: 10px;
        border-radius: 6px;
        overflow-y: auto;
        max-height: 400px;
      }
      .mineru-saas-no-data {
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
    raw = f"[MinerU SaaS Error] {error_title}\n\n文件: {filename}\n{error_detail}"
    html = f'''
    <div style="padding:16px;background:rgba(239,68,68,0.06);border-radius:8px;border:1px solid rgba(239,68,68,0.2)">
      <div style="font-size:0.9rem;font-weight:600;color:#ef4444;margin-bottom:8px">{error_title}</div>
      <div style="font-size:0.82rem;color:#64748b;line-height:1.7">
        <p>文件: <code>{filename}</code></p>
        <p>解析引擎: MinerU SaaS</p>
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