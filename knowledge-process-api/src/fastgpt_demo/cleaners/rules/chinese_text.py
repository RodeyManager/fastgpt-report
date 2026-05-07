from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class RemoveChineseSpaceRule(CleanRule):
    name = "remove_chinese_space"
    description = "移除中文字符之间的多余空格"
    default_enabled = True

    _RE = re.compile(r"([\u4e00-\u9fa5])[^\S\n]+([\u4e00-\u9fa5])")

    def apply(self, text: str, **kwargs) -> str:
        return self._RE.sub(r"\1\2", text)


register(RemoveChineseSpaceRule())
