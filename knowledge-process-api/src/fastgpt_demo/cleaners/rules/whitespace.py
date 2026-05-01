from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class TrimRule(CleanRule):
    name = "trim"
    description = "移除文本开头和结尾的空白字符"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        return text.strip()


class NormalizeNewlineRule(CleanRule):
    name = "normalize_newline"
    description = "将 Windows/旧 Mac 换行符统一为 Unix 格式"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        return text


class CollapseWhitespaceRule(CleanRule):
    name = "collapse_whitespace"
    description = "将 2 个及以上连续非换行空白字符合并为 1 个空格"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        return re.sub(r"[^\S\n]{2,}", " ", text)


class RemoveEmptyLinesRule(CleanRule):
    name = "remove_empty_lines"
    description = "将 3 行及以上连续换行压缩为 2 行"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        return re.sub(r"\n{3,}", "\n\n", text)


register(TrimRule())
register(NormalizeNewlineRule())
register(CollapseWhitespaceRule())
register(RemoveEmptyLinesRule())
