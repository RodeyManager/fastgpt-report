from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class FilterSpecialCharsRule(CleanRule):
    name = "filter_special_chars"
    description = "仅保留中文、英文、数字、常用标点和括号，移除异常符号"
    default_enabled = False

    _ALLOWED_RE = re.compile(
        r"[^\u4e00-\u9fa5"
        r"a-zA-Z0-9"
        r"\s"
        r"，。！？；：\"\"''、…—·"
        r",\.!?;:'\"`~"
        r"\-_=+\[\]{}()"
        r"<>@#\$%\^&\*/\\|"
        r"\u3000"
        r"\n\r\t"
        r"]"
    )

    def apply(self, text: str, **kwargs) -> str:
        return self._ALLOWED_RE.sub("", text)


register(FilterSpecialCharsRule())
