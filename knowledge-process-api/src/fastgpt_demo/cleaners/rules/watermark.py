from __future__ import annotations

import re
from collections import Counter

from ..base import CleanRule
from ..registry import register


class FilterWatermarkRule(CleanRule):
    name = "filter_watermark"
    description = "过滤文档中的水印文本（重复短行、关键词匹配）"
    default_enabled = False

    BUILTIN_WATERMARKS = [
        "CONFIDENTIAL", "DRAFT", "INTERNAL", "SAMPLE",
        "DO NOT DISTRIBUTE", "WATERMARK", "COPYRIGHT",
        "\u673a\u5bc6", "\u5185\u90e8\u6587\u4ef6", "\u8349\u7a3f", "\u6837\u672c",
        "\u4ec5\u4f9b\u53c2\u8003", "\u4fdd\u5bc6", "\u7981\u6b62\u4f20\u64ad",
    ]

    def apply(self, text: str, **kwargs) -> str:
        watermark_keywords = kwargs.get("watermark_keywords", [])
        min_repeat = kwargs.get("watermark_min_repeat", 2)
        max_line_len = kwargs.get("watermark_max_line_length", 30)

        all_keywords = list(self.BUILTIN_WATERMARKS) + list(watermark_keywords)

        lines = text.split("\n")
        stripped_counts = Counter(line.strip() for line in lines if line.strip())

        watermark_lines: set[str] = set()

        for line, count in stripped_counts.items():
            if count >= min_repeat and len(line) <= max_line_len:
                watermark_lines.add(line)

        for line in stripped_counts:
            if len(line) > max_line_len:
                continue
            for kw in all_keywords:
                pattern = r"(?:^|\s)" + re.escape(kw) + r"(?:\s|$)"
                if re.search(pattern, line, re.IGNORECASE):
                    watermark_lines.add(line)
                    break

        result_lines = [line for line in lines if line.strip() not in watermark_lines]
        return "\n".join(result_lines)


register(FilterWatermarkRule())
