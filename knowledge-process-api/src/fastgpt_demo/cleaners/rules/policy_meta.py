from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register

_META_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(投保单号[：:]\s*)([A-Za-z0-9_-]{5,50})"), r"\1[META:app_no]\2[/META]"),
    (re.compile(r"(保险单号[：:]\s*)([A-Za-z0-9_-]{5,50})"), r"\1[META:policy_no]\2[/META]"),
    (re.compile(r"(保单[号号][：:]\s*)([A-Za-z0-9_-]{5,50})"), r"\1[META:policy_no]\2[/META]"),
    (re.compile(r"(合同编号[：:]\s*)([A-Za-z0-9_-]{5,50})"), r"\1[META:contract_no]\2[/META]"),
    (re.compile(r"(批单号[：:]\s*)([A-Za-z0-9_-]{5,50})"), r"\1[META:endorsement_no]\2[/META]"),
    (re.compile(r"(被保险[人人][：:]\s*)([^\n]{2,30})"), r"\1[META:insured]\2[/META]"),
    (re.compile(r"(被保[人人][：:]\s*)([^\n]{2,30})"), r"\1[META:insured]\2[/META]"),
    (re.compile(r"(投保[人人][：:]\s*)([^\n]{2,30})"), r"\1[META:applicant]\2[/META]"),
]


class PreservePolicyMetaRule(CleanRule):
    name = "preserve_policy_meta"
    description = "检测保单元数据（保单号、合同编号、投保人等），用语义标记包裹"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        for pattern, replacement in _META_PATTERNS:
            text = pattern.sub(replacement, text)
        return text


register(PreservePolicyMetaRule())
