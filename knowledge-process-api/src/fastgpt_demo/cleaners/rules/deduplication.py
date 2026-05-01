from __future__ import annotations

import hashlib
from difflib import SequenceMatcher

from ..base import CleanRule
from ..registry import register


class DeduplicateParagraphsRule(CleanRule):
    name = "deduplicate_paragraphs"
    description = "检测并移除重复段落（精确匹配 + 可选模糊匹配）"
    default_enabled = False

    def apply(self, text: str, **kwargs) -> str:
        enable_fuzzy = kwargs.get("dedup_fuzzy", False)
        fuzzy_threshold = kwargs.get("dedup_fuzzy_threshold", 0.9)

        paragraphs = text.split("\n\n")
        seen_hashes: set[str] = set()
        seen_texts: list[str] = []
        unique_paragraphs: list[str] = []

        for para in paragraphs:
            stripped = para.strip()
            if not stripped:
                unique_paragraphs.append(para)
                continue

            h = hashlib.sha256(stripped.encode()).hexdigest()
            if h in seen_hashes:
                continue

            if enable_fuzzy:
                is_similar = False
                for existing in seen_texts:
                    similarity = SequenceMatcher(None, stripped, existing).ratio()
                    if similarity >= fuzzy_threshold:
                        is_similar = True
                        break
                if is_similar:
                    continue
                seen_texts.append(stripped)

            seen_hashes.add(h)
            unique_paragraphs.append(para)

        return "\n\n".join(unique_paragraphs)


register(DeduplicateParagraphsRule())
