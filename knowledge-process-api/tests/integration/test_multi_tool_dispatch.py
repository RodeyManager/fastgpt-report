"""Tests for convert_to_markdown_multi() — multi-tool dispatch with timing."""

import pytest

from fastgpt_demo.converters.markdown_converter import convert_to_markdown_multi


def test_single_markdownify():
    results = convert_to_markdown_multi("<h1>Hi</h1>", "", "html", ["markdownify"])
    assert len(results) == 1
    assert results[0]["tool"] == "markdownify"
    assert "Hi" in results[0]["markdown"]
    assert results[0]["duration_ms"] > 0


def test_both_tools():
    results = convert_to_markdown_multi("<h1>Hi</h1>", "", "html", ["markdownify", "markitdown"])
    assert len(results) == 2
    assert results[0]["tool"] == "markdownify"
    assert results[1]["tool"] == "markitdown"
    assert "Hi" in results[0]["markdown"]
    assert "Hi" in results[1]["markdown"]
    assert results[0]["duration_ms"] > 0
    assert results[1]["duration_ms"] > 0


def test_single_markitdown():
    results = convert_to_markdown_multi("<h1>Hi</h1>", "", "html", ["markitdown"])
    assert len(results) == 1
    assert results[0]["tool"] == "markitdown"


def test_docx_extension():
    results = convert_to_markdown_multi("<h1>Doc</h1>", "", "docx", ["markdownify"])
    assert len(results) == 1
    assert "Doc" in results[0]["markdown"]
    assert "DOCX" in results[0]["note"]


def test_passthrough_for_tables():
    results = convert_to_markdown_multi("raw", "| a |\n| --- |", "csv", ["markdownify"])
    assert len(results) == 1
    assert results[0]["markdown"] == "| a |\n| --- |"


def test_default_tools_parameter():
    # When tools is None, should default to ["markdownify"]
    results = convert_to_markdown_multi("<h1>Hi</h1>", "", "html", None)
    assert len(results) == 1
    assert results[0]["tool"] == "markdownify"
