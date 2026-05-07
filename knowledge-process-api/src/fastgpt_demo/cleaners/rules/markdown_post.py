from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class CleanMarkdownLinksRule(CleanRule):
    name = "clean_markdown_links"
    description = "移除 Markdown 链接文本中的换行"
    default_enabled = True

    _LINK_RE = re.compile(r"\[([^\]]+)\]\((.+?)\)")

    def apply(self, text: str, **kwargs) -> str:
        def _clean_link(m: re.Match) -> str:
            link_text = m.group(1).replace("\n", "")
            url = m.group(2)
            if not url:
                return link_text
            return f"[{link_text}]({url})"
        return self._LINK_RE.sub(_clean_link, text)


class RemoveMdEscapesRule(CleanRule):
    name = "remove_md_escapes"
    description = "移除不必要的 Markdown 反斜杠转义"
    default_enabled = True

    _UNESCAPE_RE = re.compile(r"\\([#`!*+\-\_[\]{}\\.()])")

    def apply(self, text: str, **kwargs) -> str:
        if not self._UNESCAPE_RE.search(text):
            return text
        return self._UNESCAPE_RE.sub(r"\1", text)


class CleanMdStructureRule(CleanRule):
    name = "clean_md_structure"
    description = "移除 Markdown 结构元素前的多余空格"
    default_enabled = True

    _STRUCTURE_PATTERNS = ["####", "###", "##", "#", "```", "~~~"]

    def apply(self, text: str, **kwargs) -> str:
        for pattern in self._STRUCTURE_PATTERNS:
            if re.search(r"\n\s*" + re.escape(pattern), text):
                text = re.sub(
                    r"\n( *)(" + re.escape(pattern) + r")",
                    r"\n\2",
                    text,
                )
        return text


register(CleanMarkdownLinksRule())
register(RemoveMdEscapesRule())
register(CleanMdStructureRule())
