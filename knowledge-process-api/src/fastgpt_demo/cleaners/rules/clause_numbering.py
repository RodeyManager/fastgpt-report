from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


_L1_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^(第[零一二三四五六七八九十百0-9]+条)"), r"\1[L1]"),
    (re.compile(r"^(第[零一二三四五六七八九十百0-9]+章)"), r"\1[L1]"),
    (re.compile(r"^(第[零一二三四五六七八九十百0-9]+节)"), r"\1[L1]"),
    (re.compile(r"^(第[零一二三四五六七八九十百0-9]+款)"), r"\1[L1]"),
    (re.compile(r"^(第[零一二三四五六七八九十百0-9]+项)"), r"\1[L2]"),
]

_L2_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^([零一二三四五六七八九十]+、)"), r"\1[L2]"),
    (re.compile(r"^(（[零一二三四五六七八九十]+）)"), r"\1[L2]"),
]

_L3_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^(\d+\.\d+(?:\s|$))"), r"\1[L3]"),
    (re.compile(r"^(\d+\.\s)"), r"\1[L3]"),
    (re.compile(r"^([①-⑳])"), r"\1[L3]"),
]

_ROMAN_PATTERN = re.compile(r"^([IVX]+[\.、])\s")


class NormalizeClauseNumberingRule(CleanRule):
    name = "normalize_clause_numbering"
    description = "检测保险条款的层级编号体系，在原编号后附加层级标记 [L1]/[L2]/[L3]"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        result: list[str] = []
        for line in lines:
            result.append(self._tag_clause_line(line))
        return "\n".join(result)

    def _tag_clause_line(self, line: str) -> str:
        if not line.strip():
            return line

        leading = ""
        content = line
        m = re.match(r"^(\s+)", line)
        if m:
            leading = m.group(1)
            content = line[m.end():]

        for pattern, replacement in _L1_PATTERNS:
            if pattern.match(content):
                return leading + pattern.sub(replacement, content, count=1)

        for pattern, replacement in _L2_PATTERNS:
            if pattern.match(content):
                return leading + pattern.sub(replacement, content, count=1)

        if _ROMAN_PATTERN.match(content):
            return leading + _ROMAN_PATTERN.sub(r"\1[L1]", content, count=1)

        for pattern, replacement in _L3_PATTERNS:
            if pattern.match(content):
                return leading + pattern.sub(replacement, content, count=1)

        return line


register(NormalizeClauseNumberingRule())
