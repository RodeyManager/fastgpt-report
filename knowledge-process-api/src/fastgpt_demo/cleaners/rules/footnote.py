from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class ProcessFootnotesRule(CleanRule):
    name = "process_footnotes"
    description = "识别脚注/尾注，可选保留或移除"
    default_enabled = False

    _FOOTNOTE_LINE_RE = re.compile(r"^(\[\d+\]|\^\d+|[①②③④⑤⑥⑦⑧⑨⑩])\s*.+$")

    def apply(self, text: str, **kwargs) -> str:
        action = kwargs.get("footnote_action", "remove")

        if action == "keep":
            return text

        lines = text.split("\n")
        result_lines = [line for line in lines if not self._is_footnote_line(line)]
        return "\n".join(result_lines)

    def _is_footnote_line(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        if self._FOOTNOTE_LINE_RE.match(stripped):
            return True
        return False


register(ProcessFootnotesRule())
