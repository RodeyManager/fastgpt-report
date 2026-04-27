"""MinerU document parser — placeholder mode with optional API integration."""

from __future__ import annotations

import os

from ._types import ParseResult

# MinerU supported file extensions
SUPPORTED_MINERU_EXTS = {".pdf", ".docx", ".doc", ".pptx", ".png", ".jpg", ".jpeg", ".gif", ".webp"}


def parse(buffer: bytes, filename: str) -> ParseResult:
    """Parse document using MinerU engine.

    If MINERU_API_URL is set, calls the real MinerU API.
    Otherwise returns placeholder data for testing.
    """
    from pathlib import PurePosixPath

    ext = PurePosixPath(filename).suffix.lower()
    if ext not in SUPPORTED_MINERU_EXTS:
        raise ValueError(
            f"MinerU does not support {ext} files. "
            f"Supported: {', '.join(sorted(SUPPORTED_MINERU_EXTS))}"
        )

    api_url = os.environ.get("MINERU_API_URL")

    if api_url:
        return _call_mineru_api(buffer, filename, api_url)
    else:
        return _placeholder(buffer, filename)


def _placeholder(buffer: bytes, filename: str) -> ParseResult:
    """Return placeholder data when MinerU API is not configured."""
    raw = (
        f"[MinerU Placeholder] 这是由 MinerU 解析引擎生成的模拟数据。\n"
        f"实际使用时将调用 MinerU API 服务。\n\n"
        f"文件: {filename}\n"
        f"引擎: MinerU\n\n"
        f"--- 模拟解析内容 ---\n"
        f"此文件由 MinerU 文档解析引擎处理。"
        f"MinerU 支持高质量 PDF/DOCX/PPTX 解析，"
        f"包括表格识别、公式提取、版面还原等高级功能。"
    )
    html = (
        '<div style="padding:16px;background:rgba(99,102,241,0.06);border-radius:8px;border:1px solid rgba(99,102,241,0.2)">'
        '<div style="font-size:0.9rem;font-weight:600;color:#6366f1;margin-bottom:8px">MinerU Placeholder</div>'
        '<div style="font-size:0.82rem;color:#64748b;line-height:1.7">'
        f'<p>文件: <code>{filename}</code></p>'
        f'<p>这是由 MinerU 解析引擎生成的模拟数据。实际使用时将调用 MinerU API 服务。</p>'
        f'<p>MinerU 支持高质量 PDF/DOCX/PPTX 解析，包括表格识别、公式提取、版面还原等高级功能。</p>'
        '</div></div>'
    )
    return ParseResult(
        raw_text=raw,
        format_text=raw,
        html_preview=html,
        image_list=[],
        sheet_names=None,
    )


def _call_mineru_api(buffer: bytes, filename: str, api_url: str) -> ParseResult:
    """Call real MinerU API (to be implemented when API is available)."""
    # api_key = os.environ.get("MINERU_API_KEY", "")
    # TODO: Implement real MinerU API call using httpx when API is available
    # For now, fall back to placeholder
    return _placeholder(buffer, filename)
