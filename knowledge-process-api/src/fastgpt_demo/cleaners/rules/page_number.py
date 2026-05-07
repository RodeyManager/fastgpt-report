from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class FilterPageNumbersRule(CleanRule):
    name = "filter_page_numbers"
    description = "移除独立成行的页码文本"
    default_enabled = False

    _PAGE_PATTERNS = [
        re.compile(r"^\s*\d{1,4}\s*$"),
        re.compile(r"^\s*[-—–]\s*\d{1,4}\s*[-—–]\s*$"),
        re.compile(r"^\s*第\s*\d{1,4}\s*页\s*$"),
        re.compile(r"^\s*[Pp]age\s+\d{1,4}\s*$"),
    ]

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        result_lines = [line for line in lines if not self._is_page_number(line)]
        return "\n".join(result_lines)

    def _is_page_number(self, line: str) -> bool:
        if not line.strip():
            return False
        return any(p.match(line) for p in self._PAGE_PATTERNS)


register(FilterPageNumbersRule())
