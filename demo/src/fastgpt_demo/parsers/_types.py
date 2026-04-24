"""Shared data types for document parsers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParseResult:
    raw_text: str
    format_text: str
    html_preview: str
    image_list: list = field(default_factory=list)
    sheet_names: Optional[list[str]] = None
