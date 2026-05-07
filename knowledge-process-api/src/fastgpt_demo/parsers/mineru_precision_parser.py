"""MinerU Precision API parser — calls official MinerU cloud service with token.

Requires MINERU_TOKEN environment variable.
Ref: https://mineru.net/apiManage/docs

Supports file upload via signed URLs:
1. Get signed upload URL
2. Upload file
3. Poll for result
4. Download and extract Markdown from result zip
"""

from __future__ import annotations

import os
import time
import zipfile
import io
from pathlib import PurePosixPath

import requests

from ._types import ParseResult

# MinerU Precision API endpoints
MINERU_BASE = "https://mineru.net/api/v4"
SUBMIT_TASK_ENDPOINT = f"{MINERU_BASE}/extract/task"
GET_UPLOAD_URL_ENDPOINT = f"{MINERU_BASE}/file-urls/batch"
QUERY_TASK_ENDPOINT = f"{MINERU_BASE}/extract/task"
QUERY_BATCH_ENDPOINT = f"{MINERU_BASE}/extract-results/batch"

# Supported file extensions for Precision API
SUPPORTED_PRECISION_EXTS = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx",
    ".png", ".jpg", ".jpeg", ".jp2", ".webp", ".gif", ".bmp"
}

# Polling config
POLL_INTERVAL = 3  # seconds
POLL_TIMEOUT = 600  # 10 minutes


def parse(buffer: bytes, filename: str) -> ParseResult:
    """Parse document using MinerU Precision API.

    Requires MINERU_TOKEN environment variable.

    Args:
        buffer: File content bytes
        filename: Original filename (used to determine file type)

    Returns:
        ParseResult with extracted text and HTML preview
    """
    ext = PurePosixPath(filename).suffix.lower()
    if ext not in SUPPORTED_PRECISION_EXTS:
        raise ValueError(
            f"MinerU Precision API does not support {ext} files. "
            f"Supported: {', '.join(sorted(SUPPORTED_PRECISION_EXTS))}"
        )

    token = os.environ.get("MINERU_TOKEN")
    if not token:
        return _error_result(
            filename,
            "MinerU Token 未配置",
            "请设置 MINERU_TOKEN 环境变量获取高精度解析能力"
        )

    # Use file upload mode (signing URL)
    return _parse_via_upload(buffer, filename, token)


def _parse_via_upload(buffer: bytes, filename: str, token: str) -> ParseResult:
    """Upload file to MinerU Precision API and poll for result."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Get signed upload URL
        file_payload = {
            "files": [{"name": filename}],
            "model_version": "vlm"
        }

        resp = requests.post(GET_UPLOAD_URL_ENDPOINT, headers=headers, json=file_payload, timeout=30)
        if resp.status_code == 401 or resp.status_code == 403:
            return _error_result(
                filename,
                "MinerU Token 无效或已过期",
                "请检查 MINERU_TOKEN 是否正确，或前往 mineru.net 更新 Token"
            )
        if resp.status_code == 429:
            return _error_result(
                filename,
                "MinerU 请求过于频繁",
                "请稍后再试或降低请求频率"
            )

        result = resp.json()
        if result.get("code") != 0:
            return _error_result(
                filename,
                f"MinerU API 错误 (code={result.get('code')})",
                result.get("msg", "未知错误")
            )

        batch_id = result["data"]["batch_id"]
        upload_urls = result["data"]["file_urls"]
        if not upload_urls:
            return _error_result(filename, "获取上传链接失败", "服务器未返回上传 URL")

        upload_url = upload_urls[0]

        # Step 2: Upload file to signed URL
        upload_resp = requests.put(upload_url, data=buffer, timeout=120)
        if upload_resp.status_code not in (200, 201):
            return _error_result(
                filename,
                "文件上传失败",
                f"HTTP {upload_resp.status_code}"
            )

        print(f"MinerU Precision: 文件已上传, batch_id: {batch_id}")

        # Step 3: Poll for result
        return _poll_result(filename, batch_id, headers)

    except requests.exceptions.ConnectionError:
        return _error_result(
            filename,
            "无法连接到 MinerU 服务",
            "请检查网络连接或稍后重试"
        )
    except requests.exceptions.Timeout:
        return _error_result(filename, "请求超时", "文件可能太大或服务响应慢")
    except Exception as e:
        return _error_result(filename, f"MinerU Precision 解析失败: {str(e)}", str(e))


def _poll_result(filename: str, batch_id: str, headers: dict) -> ParseResult:
    """Poll MinerU Precision API until task completes or times out."""
    state_labels = {
        "waiting-file": "等待文件上传",
        "pending": "排队中",
        "running": "解析中",
        "converting": "格式转换中",
    }

    start_time = time.time()
    file_state = None
    full_zip_url = None

    while time.time() - start_time < POLL_TIMEOUT:
        try:
            resp = requests.get(f"{QUERY_BATCH_ENDPOINT}/{batch_id}", headers=headers, timeout=30)
            result = resp.json()

            if result.get("code") != 0:
                return _error_result(
                    filename,
                    f"查询失败 (code={result.get('code')})",
                    result.get("msg", "未知错误")
                )

            extract_results = result["data"].get("extract_result", [])
            if not extract_results:
                return _error_result(filename, "未获取到解析结果", "服务器返回空结果")

            # Get first file result
            file_result = extract_results[0]
            file_state = file_result.get("state")
            elapsed = int(time.time() - start_time)

            if file_state == "done":
                full_zip_url = file_result.get("full_zip_url")
                if not full_zip_url:
                    return _error_result(filename, "解析完成但无结果链接", "服务器未返回结果 URL")
                print(f'MinerU Precision: 解析完成, zip_url: {full_zip_url}')
                md_content = _download_and_extract_markdown(filename, full_zip_url)
                return _build_result(filename, md_content)

            if file_state == "failed":
                err_msg = file_result.get("err_msg", "未知错误")
                return _error_result(
                    filename,
                    f"MinerU Precision 解析失败",
                    err_msg
                )

            # Still processing
            label = state_labels.get(file_state, file_state)
            print(f"MinerU Precision [{elapsed}s]: {label}...")

        except requests.exceptions.RequestException as e:
            return _error_result(filename, "轮询请求失败", str(e))

        time.sleep(POLL_INTERVAL)

    return _error_result(
        filename,
        "轮询超时",
        f"等待 {POLL_TIMEOUT} 秒后未获取结果，batch_id: {batch_id}"
    )


def _download_and_extract_markdown(filename: str, zip_url: str) -> str:
    """Download result zip and extract markdown content."""
    try:
        # Download zip file
        zip_resp = requests.get(zip_url, timeout=120)
        if zip_resp.status_code != 200:
            return f"[Error: 无法下载结果文件，HTTP {zip_resp.status_code}]"

        # Extract markdown from zip
        try:
            with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as zf:
                # Look for full.md (main markdown result)
                md_filename = None
                for name in zf.namelist():
                    if name.endswith('full.md'):
                        md_filename = name
                        break

                if md_filename:
                    with zf.open(md_filename) as md_file:
                        content = md_file.read()
                        # Try UTF-8 with different encodings
                        for enc in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']:
                            try:
                                return content.decode(enc)
                            except (UnicodeDecodeError, LookupError):
                                continue
                        return content.decode('latin-1')
                else:
                    # No full.md found, list available files
                    available = ', '.join(zf.namelist()[:10])
                    return f"[Error: ZIP 中未找到 full.md 文件，可用文件: {available}]"

        except zipfile.BadZipFile:
            return f"[Error: 下载的文件不是有效的 ZIP 格式]"

    except requests.exceptions.RequestException as e:
        return f"[Error: 下载结果失败: {str(e)}]"
    except Exception as e:
        return f"[Error: 提取 Markdown 失败: {str(e)}]"


def _build_result(filename: str, md_content: str) -> ParseResult:
    """Build successful ParseResult."""
    # Check for empty or very short content
    if not md_content or len(md_content.strip()) < 10:
        return _error_result(
            filename,
            "MinerU Precision 返回内容为空",
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
    """Build HTML preview showing MinerU Precision Markdown content."""
    sections = []

    # Header
    sections.append(f'''
    <div class="mineru-precision-preview">
      <div class="mineru-precision-header">
        <span class="mineru-precision-badge">MinerU Precision</span>
        <span class="mineru-precision-file">{filename}</span>
      </div>
      <div class="mineru-precision-content">
    ''')

    # Show markdown content
    if md_content:
        sections.append(_escape_html(md_content))
    else:
        sections.append(f'''
        <div class="mineru-precision-no-data">MinerU Precision 未返回 Markdown 内容</div>
        ''')

    sections.append('</div></div>')

    # Add styles
    sections.append('''
    <style>
      .mineru-precision-preview {
        padding: 12px;
        background: rgba(139, 92, 246, 0.04);
        border-radius: 8px;
        border: 1px solid rgba(139, 92, 246, 0.15);
      }
      .mineru-precision-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(139, 92, 246, 0.2);
      }
      .mineru-precision-badge {
        background: linear-gradient(135deg, #8b5cf6, #a78bfa);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
      }
      .mineru-precision-file {
        font-size: 0.82rem;
        color: #64748b;
      }
      .mineru-precision-content {
        font-size: 0.82rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
        padding: 10px;
        border-radius: 6px;
        overflow-y: auto;
        max-height: 400px;
      }
      .mineru-precision-no-data {
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
    raw = f"[MinerU Precision Error] {error_title}\n\n文件: {filename}\n{error_detail}"
    html = f'''
    <div style="padding:16px;background:rgba(239,68,68,0.06);border-radius:8px;border:1px solid rgba(239,68,68,0.2)">
      <div style="font-size:0.9rem;font-weight:600;color:#ef4444;margin-bottom:8px">{error_title}</div>
      <div style="font-size:0.82rem;color:#64748b;line-height:1.7">
        <p>文件: <code>{filename}</code></p>
        <p>解析引擎: MinerU Precision API</p>
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