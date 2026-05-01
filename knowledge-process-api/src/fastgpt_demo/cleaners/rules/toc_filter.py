from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class FilterTocRule(CleanRule):
    name = "filter_toc"
    description = "检测并移除自动生成的目录区域（需 ≥3 行连续目录条目）"
    default_enabled = False

    _TOC_PATTERNS = [
        re.compile(r"^\d+(\.\d+)*\s+.+\s*\.{2,}\s*\d+\s*$"),
        re.compile(r"^第[一二三四五六七八九十\d]+[章节篇]\s+.+$"),
        re.compile(r"^附录\s*[A-Z\d]*\s+.+$"),
    ]

    _MIN_CONSECUTIVE = 3

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        is_toc_line = [self._match_toc(line) for line in lines]

        result_lines = []
        i = 0
        while i < len(lines):
            if is_toc_line[i]:
                run_start = i
                while i < len(lines) and is_toc_line[i]:
                    i += 1
                run_len = i - run_start
                if run_len < self._MIN_CONSECUTIVE:
                    for j in range(run_start, i):
                        result_lines.append(lines[j])
            else:
                result_lines.append(lines[i])
                i += 1

        return "\n".join(result_lines)

    def _match_toc(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        for pattern in self._TOC_PATTERNS:
            if pattern.match(stripped):
                return True
        return False


register(FilterTocRule())
