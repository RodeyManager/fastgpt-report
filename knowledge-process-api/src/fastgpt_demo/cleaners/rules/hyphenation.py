from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class FixHyphenationRule(CleanRule):
    name = "fix_hyphenation"
    description = "修复 PDF 提取中因断行产生的连字符分割"
    default_enabled = True

    _RE = re.compile(r"(\w)-\n(\w)")

    def apply(self, text: str, **kwargs) -> str:
        return self._RE.sub(r"\1\2", text)


register(FixHyphenationRule())
