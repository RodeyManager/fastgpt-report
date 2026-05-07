from __future__ import annotations

from .base import CleanProfile
from .default import DEFAULT_RULES, DEFAULT_PARAMS


def create_profile() -> CleanProfile:
    rules = {**DEFAULT_RULES, "filter_watermark": True, "filter_page_numbers": True}
    return CleanProfile(name="pdf_business", description="商务 PDF", rules=rules, params=DEFAULT_PARAMS)
