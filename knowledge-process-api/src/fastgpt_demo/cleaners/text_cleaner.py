"""Text cleaning utilities — re-exports from converters for convenience."""

from __future__ import annotations

from fastgpt_demo.converters.markdown_converter import (
    fastgpt_simple_text,
    simple_markdown_text,
    simple_text,
)

# Alias so app.py can import ``clean_text`` as a top-level function.
clean_text = simple_text

__all__ = ["clean_text", "fastgpt_simple_text", "simple_markdown_text"]
