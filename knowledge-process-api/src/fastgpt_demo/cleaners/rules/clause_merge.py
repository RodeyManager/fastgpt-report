from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register

_START_RE = re.compile(r"^\s*第[零一二三四五六七八九十百0-9]+条(?:\[L1\])?\s*")


def _is_clause_start(line: str) -> bool:
    return bool(_START_RE.match(line))


def _is_sentence_end(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    return stripped[-1] in "。！？；：，、」』）\")"


class MergeBrokenClausesRule(CleanRule):
    name = "merge_broken_clauses"
    description = "合并因翻页截断的条款文本，将不完整行与续行拼接"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        result: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                result.append(line)
                i += 1
                continue

            if _is_clause_start(line):
                merged = stripped
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    if _is_clause_start(lines[j]):
                        break
                    if _is_sentence_end(merged):
                        merged += "\n" + next_line
                        j += 1
                        continue
                    merged += next_line
                    j += 1
                result.append(merged)
                i = j
            else:
                result.append(line)
                i += 1

        return "\n".join(result)


register(MergeBrokenClausesRule())
