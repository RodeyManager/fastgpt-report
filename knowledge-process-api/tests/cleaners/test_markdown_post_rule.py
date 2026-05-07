import pytest

from fastgpt_demo.cleaners.base import CleanRule
from fastgpt_demo.cleaners.registry import get, get_all_rules, clear
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners.rules.markdown_post import (
    CleanMarkdownLinksRule,
    RemoveMdEscapesRule,
    CleanMdStructureRule,
)
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401


@pytest.fixture(autouse=True)
def _clean_registry():
    clear()
    from fastgpt_demo.cleaners.rules.whitespace import TrimRule, NormalizeNewlineRule, CollapseWhitespaceRule, RemoveEmptyLinesRule
    from fastgpt_demo.cleaners.rules.unicode import NormalizeUnicodeRule
    from fastgpt_demo.cleaners.rules.chinese_text import RemoveChineseSpaceRule
    from fastgpt_demo.cleaners.rules.hyphenation import FixHyphenationRule
    from fastgpt_demo.cleaners.rules.sensitive import MaskSensitiveRule
    from fastgpt_demo.cleaners.rules.special_chars import FilterSpecialCharsRule
    from fastgpt_demo.cleaners.rules.watermark import FilterWatermarkRule
    from fastgpt_demo.cleaners.rules.deduplication import DeduplicateParagraphsRule
    from fastgpt_demo.cleaners.rules.table_clean import CleanTableRule
    from fastgpt_demo.cleaners.registry import register

    register(TrimRule())
    register(NormalizeNewlineRule())
    register(CollapseWhitespaceRule())
    register(RemoveEmptyLinesRule())
    register(NormalizeUnicodeRule())
    register(RemoveChineseSpaceRule())
    register(FixHyphenationRule())
    register(MaskSensitiveRule())
    register(FilterSpecialCharsRule())
    register(FilterWatermarkRule())
    register(DeduplicateParagraphsRule())
    register(CleanTableRule())
    register(CleanMarkdownLinksRule())
    register(RemoveMdEscapesRule())
    register(CleanMdStructureRule())
    yield
    clear()


class TestCleanMarkdownLinksRule:
    def test_removes_newlines_in_link_text(self):
        rule = get("clean_markdown_links")
        text = "[hello\nworld](http://example.com)"
        result = rule.apply(text)
        assert result == "[helloworld](http://example.com)"

    def test_preserves_link_without_newlines(self):
        rule = get("clean_markdown_links")
        text = "[hello](http://example.com)"
        result = rule.apply(text)
        assert result == "[hello](http://example.com)"

    def test_preserves_plain_text(self):
        rule = get("clean_markdown_links")
        text = "普通文本没有链接"
        result = rule.apply(text)
        assert result == "普通文本没有链接"


class TestRemoveMdEscapesRule:
    def test_removes_backslash_escapes(self):
        rule = get("remove_md_escapes")
        text = r"hello \*world\* and \#heading"
        result = rule.apply(text)
        assert result == "hello *world* and #heading"

    def test_preserves_normal_text(self):
        rule = get("remove_md_escapes")
        text = "hello world"
        result = rule.apply(text)
        assert result == "hello world"


class TestCleanMdStructureRule:
    def test_removes_leading_spaces_before_heading(self):
        rule = get("clean_md_structure")
        text = "text\n  ## heading"
        result = rule.apply(text)
        assert result == "text\n## heading"

    def test_removes_leading_spaces_before_code_block(self):
        rule = get("clean_md_structure")
        text = "text\n  ```python"
        result = rule.apply(text)
        assert result == "text\n```python"

    def test_preserves_heading_without_spaces(self):
        rule = get("clean_md_structure")
        text = "text\n## heading"
        result = rule.apply(text)
        assert result == "text\n## heading"


class TestMarkdownPostInPipeline:
    def test_pipeline_applies_markdown_post_rules(self):
        pipeline = CleanPipeline()
        text = "[hello\nworld](url)  \\*bold\\*  \n  ## heading"
        result = pipeline.execute(text, {
            "clean_markdown_links": True,
            "remove_md_escapes": True,
            "clean_md_structure": True,
        })
        assert "\\*" not in result
        assert "## heading" in result
