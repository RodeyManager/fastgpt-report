"""Text cleaning utilities — delegates to CleanPipeline for rule-based cleaning."""

from __future__ import annotations

from fastgpt_demo.converters.markdown_converter import (
    fastgpt_simple_text,
    simple_markdown_text,
)
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401 — trigger registration
from fastgpt_demo.cleaners.profiles import get_profile  # noqa: F401

_pipeline = CleanPipeline()


def simple_text(text: str, options: dict | None = None, profile: str = "default") -> str:
    opts = options or {}
    if not opts and profile != "default":
        p = get_profile(profile)
        if p:
            opts = p.to_options_dict()
    return _pipeline.execute(text, opts)


clean_text = simple_text

__all__ = ["clean_text", "fastgpt_simple_text", "simple_markdown_text", "simple_text"]
