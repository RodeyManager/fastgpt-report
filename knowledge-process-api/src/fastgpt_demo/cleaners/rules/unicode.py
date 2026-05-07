from __future__ import annotations

import re
import unicodedata

from ..base import CleanRule
from ..registry import register


class NormalizeUnicodeRule(CleanRule):
    name = "normalize_unicode"
    description = "使用 NFKC 形式统一全角/半角字符和兼容性字符"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        return unicodedata.normalize("NFKC", text)


class RemoveInvisibleCharsRule(CleanRule):
    name = "remove_invisible_chars"
    description = "移除零宽空格、BOM、软连字符等不可见 Unicode 字符"
    default_enabled = True

    _INVISIBLE_RE = re.compile(
        r"[\u200b\u200c\u200d\u200e\u200f\u00ad\u034f\u061c\u180e\ufeff\ufff9\ufffa\ufffb]"
    )

    def apply(self, text: str, **kwargs) -> str:
        return self._INVISIBLE_RE.sub("", text)


register(NormalizeUnicodeRule())
register(RemoveInvisibleCharsRule())
