from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile

DEFAULT_RULES = {
    "trim": True, "normalize_unicode": True, "remove_invisible_chars": True,
    "remove_chinese_space": True, "normalize_newline": True, "fix_hyphenation": True,
    "collapse_whitespace": True, "remove_empty_lines": True,
    "remove_html_comments": False, "normalize_html_entities": False,
    "filter_html_noise": False, "filter_watermark": False,
    "filter_toc": False, "filter_page_numbers": False,
    "process_footnotes": False, "deduplicate_paragraphs": False,
    "clean_table": False, "clean_markdown_links": True,
    "remove_md_escapes": True, "clean_md_structure": True,
    "mask_sensitive": False, "filter_special_chars": False,
}

DEFAULT_PARAMS = {
    "watermark_keywords": [], "watermark_min_repeat": 2, "watermark_max_line_length": 30,
    "dedup_fuzzy": False, "dedup_fuzzy_threshold": 0.9,
    "footnote_action": "remove",
    "html_noise_patterns": [], "html_ad_keywords": [],
}


def create_profile() -> CleanProfile:
    return CleanProfile(
        name="default", description="通用文档", rules=DEFAULT_RULES, params=DEFAULT_PARAMS,
    )
