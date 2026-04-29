"""Tests for ConvertRequest / ToolResult / ConvertResponse models (multi-tool support)."""

import pytest
from pydantic import ValidationError

from app import ConvertRequest, ConvertResponse, ToolResult


# ---------------------------------------------------------------------------
# ConvertRequest — defaults & valid inputs
# ---------------------------------------------------------------------------

def test_convert_request_default_tools():
    """ConvertRequest with no tools arg defaults to ["markdownify"]."""
    req = ConvertRequest(raw_text="hello", format_text="<p>hello</p>", file_ext="html")
    assert req.tools == ["markdownify"]


def test_convert_request_custom_tools():
    """ConvertRequest accepts tools=["markdownify", "markitdown"]."""
    req = ConvertRequest(
        raw_text="hello",
        format_text="<p>hello</p>",
        file_ext="html",
        tools=["markdownify", "markitdown"],
    )
    assert req.tools == ["markdownify", "markitdown"]


def test_convert_request_single_markitdown():
    """ConvertRequest accepts tools=["markitdown"]."""
    req = ConvertRequest(
        raw_text="hello",
        format_text="<p>hello</p>",
        file_ext="html",
        tools=["markitdown"],
    )
    assert req.tools == ["markitdown"]


# ---------------------------------------------------------------------------
# ConvertRequest — validation errors
# ---------------------------------------------------------------------------

def test_convert_request_invalid_tool_name():
    """ConvertRequest with tools=["unknown"] raises ValidationError."""
    with pytest.raises(ValidationError):
        ConvertRequest(
            raw_text="hello",
            format_text="<p>hello</p>",
            file_ext="html",
            tools=["unknown"],
        )


def test_convert_request_too_many_tools():
    """ConvertRequest with 3 tools raises ValidationError."""
    with pytest.raises(ValidationError):
        ConvertRequest(
            raw_text="hello",
            format_text="<p>hello</p>",
            file_ext="html",
            tools=["markdownify", "markitdown", "other"],
        )


def test_convert_request_empty_tools():
    """ConvertRequest with empty tools list raises ValidationError."""
    with pytest.raises(ValidationError):
        ConvertRequest(
            raw_text="hello",
            format_text="<p>hello</p>",
            file_ext="html",
            tools=[],
        )


# ---------------------------------------------------------------------------
# ToolResult model
# ---------------------------------------------------------------------------

def test_tool_result_model():
    """ToolResult has all required fields."""
    result = ToolResult(
        tool="markdownify",
        markdown="# Hello",
        note="converted ok",
        duration_ms=42.5,
    )
    assert result.tool == "markdownify"
    assert result.markdown == "# Hello"
    assert result.note == "converted ok"
    assert result.duration_ms == 42.5


# ---------------------------------------------------------------------------
# ConvertResponse model
# ---------------------------------------------------------------------------

def test_convert_response_model():
    """ConvertResponse has results field accepting list of ToolResult."""
    result = ToolResult(
        tool="markdownify",
        markdown="# Hello",
        note="ok",
        duration_ms=10.0,
    )
    resp = ConvertResponse(results=[result])
    assert len(resp.results) == 1
    assert resp.results[0].tool == "markdownify"
    assert resp.results[0].markdown == "# Hello"


def test_convert_response_multiple_results():
    """ConvertResponse can hold multiple ToolResult entries."""
    r1 = ToolResult(tool="markdownify", markdown="# A", note="ok", duration_ms=5.0)
    r2 = ToolResult(tool="markitdown", markdown="# B", note="ok", duration_ms=8.0)
    resp = ConvertResponse(results=[r1, r2])
    assert len(resp.results) == 2
