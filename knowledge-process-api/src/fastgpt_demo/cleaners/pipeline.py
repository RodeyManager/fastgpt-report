from __future__ import annotations

import re

from .base import CleanRule
from .registry import get_all_rules


def _replace_control_chars(text: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)


class CleanPipeline:
    def __init__(self, rules: list[CleanRule] | None = None):
        self.rules: list[CleanRule] = rules if rules is not None else get_all_rules()

    def execute(self, text: str, options: dict | None = None) -> str:
        opts = options or {}
        for rule in self.rules:
            if rule.should_run(opts):
                text = rule.apply(text, **opts)
        text = _replace_control_chars(text)
        return text
