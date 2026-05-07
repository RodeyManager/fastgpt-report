import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.html_clean import (
    RemoveHtmlCommentsRule, NormalizeHtmlEntitiesRule, FilterHtmlNoiseRule,
)


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(RemoveHtmlCommentsRule())
    register(NormalizeHtmlEntitiesRule())
    register(FilterHtmlNoiseRule())
    yield
    clear()


class TestRemoveHtmlCommentsRule:
    def test_removes_html_comment(self):
        rule = get("remove_html_comments")
        text = "before<!-- comment -->after"
        result = rule.apply(text)
        assert result == "beforeafter"

    def test_removes_multiline_comment(self):
        rule = get("remove_html_comments")
        text = "before<!-- line1\nline2 -->after"
        result = rule.apply(text)
        assert result == "beforeafter"

    def test_preserves_text_without_comments(self):
        rule = get("remove_html_comments")
        text = "普通文本"
        result = rule.apply(text)
        assert result == "普通文本"


class TestNormalizeHtmlEntitiesRule:
    def test_converts_common_entities(self):
        rule = get("normalize_html_entities")
        text = "&amp; &lt; &gt; &quot;"
        result = rule.apply(text)
        assert result == '& < > "'

    def test_converts_nbsp(self):
        rule = get("normalize_html_entities")
        text = "hello&nbsp;world"
        result = rule.apply(text)
        assert result == "hello world"

    def test_converts_decimal_reference(self):
        rule = get("normalize_html_entities")
        text = "&#65;&#66;"
        result = rule.apply(text)
        assert result == "AB"

    def test_converts_hex_reference(self):
        rule = get("normalize_html_entities")
        text = "&#x41;&#x42;"
        result = rule.apply(text)
        assert result == "AB"

    def test_converts_chinese_entities(self):
        rule = get("normalize_html_entities")
        text = "&copy; &reg; &trade;"
        result = rule.apply(text)
        assert result == "© ® ™"


class TestFilterHtmlNoiseRule:
    def test_removes_copyright(self):
        rule = get("filter_html_noise")
        text = "正文内容\ncopyright © 2024 公司名\n更多正文"
        result = rule.apply(text)
        assert "copyright" not in result
        assert "正文内容" in result

    def test_removes_icp(self):
        rule = get("filter_html_noise")
        text = "正文内容\n沪ICP备12345678号\n更多正文"
        result = rule.apply(text)
        assert "沪ICP" not in result

    def test_removes_disclaimer(self):
        rule = get("filter_html_noise")
        text = "正文内容\n免责声明：本文仅供参考\n更多正文"
        result = rule.apply(text)
        assert "免责声明" not in result

    def test_preserves_normal_text(self):
        rule = get("filter_html_noise")
        text = "普通文本没有噪声"
        result = rule.apply(text)
        assert result == "普通文本没有噪声"

    def test_custom_noise_patterns(self):
        rule = get("filter_html_noise")
        text = "正文\n自定义噪声行\n更多正文"
        result = rule.apply(text, html_noise_patterns=[r"自定义噪声.*"])
        assert "自定义噪声行" not in result

    def test_preserves_empty_lines(self):
        rule = get("filter_html_noise")
        text = "正文\n\n更多正文"
        result = rule.apply(text)
        assert "\n\n" in result
