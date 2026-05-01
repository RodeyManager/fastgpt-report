from __future__ import annotations

from .base import CleanProfile
from .default import DEFAULT_RULES, DEFAULT_PARAMS


def create_profile() -> CleanProfile:
    rules = {**DEFAULT_RULES, "filter_toc": True, "process_footnotes": True}
    params = {**DEFAULT_PARAMS, "footnote_action": "keep"}
    return CleanProfile(name="legal", description="法律文书", rules=rules, params=params)
