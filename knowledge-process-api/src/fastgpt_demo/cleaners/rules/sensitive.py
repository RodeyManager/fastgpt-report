from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class MaskSensitiveRule(CleanRule):
    name = "mask_sensitive"
    description = "使用占位符替换身份证号、银行卡号、护照号、军官证、手机号、邮箱、IP 地址等敏感信息"
    default_enabled = False

    _PATTERNS: list[tuple[re.Pattern, str]] = [
        (re.compile(r"[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]"), "***IDCARD***"),
        (re.compile(r"(?<!\d)(?:62|4|5|3[4-9])\d{14,17}(?!\d)"), "***BANKCARD***"),
        (re.compile(r"(?<![A-Za-z0-9])[EK]\d{8}(?![A-Za-z0-9])"), "***PASSPORT***"),
        (re.compile(r"(?<![A-Za-z0-9])\u519b\u5b57\u7b2c\d{6,8}\u53f7(?![A-Za-z0-9])"), "***MILITARY***"),
        (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "***PHONE***"),
        (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "***EMAIL***"),
        (re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"), "***IP***"),
    ]

    def apply(self, text: str, **kwargs) -> str:
        for pattern, mask in self._PATTERNS:
            text = pattern.sub(mask, text)
        return text


register(MaskSensitiveRule())
