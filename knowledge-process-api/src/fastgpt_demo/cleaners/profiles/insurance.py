from __future__ import annotations

from .base import CleanProfile
from .default import DEFAULT_RULES, DEFAULT_PARAMS

INSURANCE_RULES = {
    **DEFAULT_RULES,
    "normalize_clause_numbering": True,
    "preserve_policy_meta": True,
    "merge_broken_clauses": True,
    "fix_ocr_numbering": True,
    "filter_watermark": True,
    "filter_page_numbers": True,
    "process_footnotes": True,
    "clean_table": True,
    "clean_insurance_table": False,
    "mask_sensitive": False,
    "deduplicate_paragraphs": False,
}

INSURANCE_PARAMS = {
    **DEFAULT_PARAMS,
    "footnote_action": "keep",
    "insurance_mode": True,
}


def create_profile() -> CleanProfile:
    return CleanProfile(
        name="insurance",
        description="保险条款/保险合同专用",
        rules=INSURANCE_RULES,
        params=INSURANCE_PARAMS,
    )
