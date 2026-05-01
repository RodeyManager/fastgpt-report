from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class RemoveHtmlCommentsRule(CleanRule):
    name = "remove_html_comments"
    description = "移除 HTML 注释（<!-- ... -->）"
    default_enabled = False

    _COMMENT_RE = re.compile(r"<!--[\s\S]*?-->|<!--[\s\S]*$", re.MULTILINE)

    def apply(self, text: str, **kwargs) -> str:
        return self._COMMENT_RE.sub("", text)


class NormalizeHtmlEntitiesRule(CleanRule):
    name = "normalize_html_entities"
    description = "将 HTML 命名实体和数字引用转换为 Unicode 字符"
    default_enabled = False

    _NAMED_ENTITIES = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&apos;": "'",
        "&mdash;": "\u2014", "&ndash;": "\u2013", "&hellip;": "\u2026",
        "&copy;": "\u00a9", "&reg;": "\u00ae", "&trade;": "\u2122",
        "&lsquo;": "\u2018", "&rsquo;": "\u2019",
        "&ldquo;": "\u201c", "&rdquo;": "\u201d",
        "&deg;": "\u00b0",
    }
    _DECIMAL_RE = re.compile(r"&#(\d+);")
    _HEX_RE = re.compile(r"&#x([0-9a-fA-F]+);")

    def apply(self, text: str, **kwargs) -> str:
        for entity, char in self._NAMED_ENTITIES.items():
            text = text.replace(entity, char)
        text = self._DECIMAL_RE.sub(lambda m: chr(int(m.group(1))), text)
        text = self._HEX_RE.sub(lambda m: chr(int(m.group(1), 16)), text)
        return text


class FilterHtmlNoiseRule(CleanRule):
    name = "filter_html_noise"
    description = "移除版权声明、备案信息、广告关键词等网页噪声"
    default_enabled = False

    BUILTIN_NOISE_PATTERNS = [
        r"copyright\s*©?\s*\d{4}.*$",
        r"all\s+rights\s+reserved.*$",
        r"[沪京粤深]ICP[备证]\d+号.*$",
        r"免责声明[：:].*$",
        r"本文来源[：:].*$",
        r"责任编辑[：:].*$",
        r"[浏阅]读次数[：:]\s*\d+.*$",
    ]
    BUILTIN_AD_KEYWORDS = ["广告", "推广", "优惠", "促销", "VIP", "购买", "热线"]

    def apply(self, text: str, **kwargs) -> str:
        noise_patterns = kwargs.get("html_noise_patterns", [])
        ad_keywords = kwargs.get("html_ad_keywords", [])

        all_patterns = list(self.BUILTIN_NOISE_PATTERNS) + list(noise_patterns)
        all_ads = list(self.BUILTIN_AD_KEYWORDS) + list(ad_keywords)

        compiled = [re.compile(p, re.IGNORECASE) for p in all_patterns]

        lines = text.split("\n")
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result_lines.append(line)
                continue

            is_noise = any(p.search(stripped) for p in compiled)

            if not is_noise and all_ads:
                ad_count = sum(1 for kw in all_ads if kw in stripped)
                if ad_count > 0 and ad_count / max(len(stripped), 1) > 0.3:
                    is_noise = True

            if not is_noise:
                result_lines.append(line)

        return "\n".join(result_lines)


register(RemoveHtmlCommentsRule())
register(NormalizeHtmlEntitiesRule())
register(FilterHtmlNoiseRule())
