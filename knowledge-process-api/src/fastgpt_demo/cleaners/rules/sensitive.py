from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register

_IDCARD_RE = re.compile(r"[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]")
_BANKCARD_RE = re.compile(r"(?<!\d)(?:62|4|5|3[4-9])\d{14,17}(?!\d)")
_PASSPORT_RE = re.compile(r"(?<![A-Za-z0-9])[EK]\d{8}(?![A-Za-z0-9])")
_MILITARY_RE = re.compile(r"(?<![A-Za-z0-9])\u519b\u5b57\u7b2c\d{6,8}\u53f7(?![A-Za-z0-9])")
_PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_IP_RE = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")
_POLICY_NO_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z]{1,4})(\d{8,20})(?![A-Za-z0-9])")
_NAME_RE = re.compile(r"被保(?:险|障)?人[：:]\s*([^\n]{2,4})(?=\s|$)")

_GENERIC_PATTERNS: list[tuple[re.Pattern, str]] = [
    (_IDCARD_RE, "***IDCARD***"),
    (_BANKCARD_RE, "***BANKCARD***"),
    (_PASSPORT_RE, "***PASSPORT***"),
    (_MILITARY_RE, "***MILITARY***"),
    (_PHONE_RE, "***PHONE***"),
    (_EMAIL_RE, "***EMAIL***"),
    (_IP_RE, "***IP***"),
]


def _mask_idcard(m: re.Match) -> str:
    s = m.group()
    return s[:3] + "*" * 11 + s[-4:]


def _mask_bankcard(m: re.Match) -> str:
    s = m.group()
    return s[:4] + "*" * (len(s) - 8) + s[-4:]


def _mask_phone(m: re.Match) -> str:
    s = m.group()
    return s[:3] + "****" + s[-4:]


def _mask_email(m: re.Match) -> str:
    s = m.group()
    at_pos = s.find("@")
    if at_pos > 1:
        return s[0] + "*" * (at_pos - 1) + s[at_pos:]
    return "***@***"


def _mask_policy_no(m: re.Match) -> str:
    prefix = m.group(1)
    digits = m.group(2)
    return prefix + "*" * (len(digits) - 3) + digits[-3:]


def _mask_name(m: re.Match) -> str:
    name = m.group(1)
    if len(name) <= 1:
        return m.group()
    return m.group().replace(name, name[0] + "*" * (len(name) - 1))


class MaskSensitiveRule(CleanRule):
    name = "mask_sensitive"
    description = "使用占位符替换身份证号、银行卡号、护照号、军官证、手机号、邮箱、IP 地址等敏感信息"
    default_enabled = False

    def apply(self, text: str, **kwargs) -> str:
        insurance_mode = kwargs.get("insurance_mode", False)

        if insurance_mode:
            return self._apply_insurance_mode(text)
        return self._apply_generic_mode(text)

    @staticmethod
    def _apply_generic_mode(text: str) -> str:
        for pattern, mask in _GENERIC_PATTERNS:
            text = pattern.sub(mask, text)
        return text

    @staticmethod
    def _apply_insurance_mode(text: str) -> str:
        text = _IDCARD_RE.sub(_mask_idcard, text)
        text = _BANKCARD_RE.sub(_mask_bankcard, text)
        text = _PHONE_RE.sub(_mask_phone, text)
        text = _EMAIL_RE.sub(_mask_email, text)
        text = _POLICY_NO_RE.sub(_mask_policy_no, text)
        text = _NAME_RE.sub(_mask_name, text)
        text = _PASSPORT_RE.sub("***PASSPORT***", text)
        text = _MILITARY_RE.sub("***MILITARY***", text)
        text = _IP_RE.sub("***IP***", text)
        return text


register(MaskSensitiveRule())
