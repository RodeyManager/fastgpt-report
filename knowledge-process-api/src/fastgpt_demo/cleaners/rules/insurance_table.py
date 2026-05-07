from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register

_ANNOTATION_RE = re.compile(r"^\s*\|?\s*(注[：:]|说明[：:]|备注[：:]|注释[：:])")
_SUMMARY_RE = re.compile(r"(合[计計]|总[计計]|小[计計]|累[计計])")


class CleanInsuranceTableRule(CleanRule):
    name = "clean_insurance_table"
    description = "保险表格专项清洗：保留注释行和合计行"
    default_enabled = False

    _ROW_RE = re.compile(r"^\s*\|(?:[^\n|]*\|)+\s*$")
    _SEP_RE = re.compile(r"^\s*\|(?:[:\-\s]*\|)+\s*$")

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        result: list[str] = []
        for i, line in enumerate(lines):
            if self._is_annotation_line(line):
                if not self._is_in_table(lines, i):
                    result.append(line)
                    continue
                if line.strip().startswith("|"):
                    result.append(line)
                else:
                    if result and result[-1] == "":
                        result.pop()
                    result.append(line)
                    result.append("")
                continue

            if self._is_summary_line(line):
                result.append(line)
                continue

            result.append(line)
        return "\n".join(result)

    def _is_annotation_line(self, line: str) -> bool:
        return bool(_ANNOTATION_RE.match(line))

    @staticmethod
    def _is_summary_line(line: str) -> bool:
        return bool(_SUMMARY_RE.search(line))

    @classmethod
    def _is_in_table(cls, lines: list[str], idx: int) -> bool:
        for j in range(idx - 1, max(idx - 5, -1), -1):
            candidate = lines[j].strip()
            if not candidate:
                continue
            return bool(cls._ROW_RE.match(candidate))
        return False


register(CleanInsuranceTableRule())
