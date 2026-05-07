from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register

_CLAUSE_CTX_RE = re.compile(
    r"^(第)(\s*)([\w零一二三四五六七八九十百]+)(\s*)([条章款节项])"
)

_NUM_ZH_RE = re.compile(r"^[零一二三四五六七八九十]+、")

_PAREN_ZH_RE = re.compile(r"^（[零一二三四五六七八九十]+）")


class FixOcrNumberingRule(CleanRule):
    name = "fix_ocr_numbering"
    description = "修复扫描件 OCR 识别后的条款编号错误（l→1、O→0、英文标点→中文标点）"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        result: list[str] = []
        for line in lines:
            result.append(self._fix_line(line))
        return "\n".join(result)

    def _fix_line(self, line: str) -> str:
        m = _CLAUSE_CTX_RE.match(line)
        if m:
            prefix = m.group(1)
            space1 = m.group(2)
            num_part = m.group(3)
            space2 = m.group(4)
            suffix = m.group(5)
            num_part = self._fix_num_in_context(num_part)
            rest = line[m.end():]
            return f"{prefix}{space1}{num_part}{space2}{suffix}{rest}"

        m2 = _NUM_ZH_RE.match(line)
        if m2:
            return line

        m3 = _PAREN_ZH_RE.match(line)
        if m3:
            return line

        if re.match(r"^([一二三四五六七八九十]+)\.,\s", line):
            line = re.sub(r"^([一二三四五六七八九十]+)\.,", r"\1、", line)
        elif re.match(r"^([一二三四五六七八九十]+),\s", line):
            line = re.sub(r"^([一二三四五六七八九十]+),", r"\1、", line)
        elif re.match(r"^([一二三四五六七八九十]+)\.\s", line):
            line = re.sub(r"^([一二三四五六七八九十]+)\.", r"\1、", line)

        return line

    @staticmethod
    def _fix_num_in_context(num_str: str) -> str:
        result = num_str.replace("l", "1")
        result = result.replace("O", "0")
        result = result.replace("o", "0")
        return result


register(FixOcrNumberingRule())
