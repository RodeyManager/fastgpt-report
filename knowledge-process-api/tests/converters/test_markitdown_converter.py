"""Tests for the markitdown-based HTML-to-Markdown converter."""

from fastgpt_demo.converters import html_to_markdown_markitdown


def test_basic_html_conversion():
    result = html_to_markdown_markitdown("<h1>Hello</h1><p>World</p>")
    assert "Hello" in result
    assert "World" in result


def test_empty_input():
    result = html_to_markdown_markitdown("")
    assert result == ""


def test_table_html():
    result = html_to_markdown_markitdown("<table><tr><td>A</td></tr></table>")
    assert "A" in result


def test_heading_conversion():
    result = html_to_markdown_markitdown("<h2>Section Title</h2>")
    assert "Section Title" in result
