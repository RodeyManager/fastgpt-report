from __future__ import annotations

from .base import CleanProfile
from .default import DEFAULT_RULES, DEFAULT_PARAMS


def create_profile() -> CleanProfile:
    rules = {**DEFAULT_RULES, "remove_html_comments": True, "normalize_html_entities": True, "filter_watermark": True, "filter_html_noise": True, "clean_markdown_links": True}
    return CleanProfile(name="web_content", description="HTML 网页内容", rules=rules, params=DEFAULT_PARAMS)
