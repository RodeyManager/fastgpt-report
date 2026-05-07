from __future__ import annotations

from .base import CleanProfile
from .default import DEFAULT_RULES, DEFAULT_PARAMS


def create_profile() -> CleanProfile:
    rules = {**DEFAULT_RULES, "filter_toc": True, "filter_page_numbers": True, "process_footnotes": True}
    params = {**DEFAULT_PARAMS, "footnote_action": "keep"}
    return CleanProfile(name="pdf_academic", description="学术论文 PDF", rules=rules, params=params)
