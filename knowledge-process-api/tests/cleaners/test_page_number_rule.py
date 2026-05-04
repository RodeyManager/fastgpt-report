import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.page_number import FilterPageNumbersRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(FilterPageNumbersRule())
    yield
    clear()


class TestFilterPageNumbersRule:
    def test_removes_bare_number(self):
        rule = get("filter_page_numbers")
        text = "正文内容\n12\n更多正文"
        result = rule.apply(text)
        assert "正文内容" in result
        assert "更多正文" in result
        assert "\n12\n" not in result

    def test_removes_dashed_page_number(self):
        rule = get("filter_page_numbers")
        text = "正文\n- 5 -\n更多正文"
        result = rule.apply(text)
        assert "- 5 -" not in result

    def test_removes_chinese_page_number(self):
        rule = get("filter_page_numbers")
        text = "正文\n第 12 页\n更多正文"
        result = rule.apply(text)
        assert "第 12 页" not in result

    def test_removes_english_page_number(self):
        rule = get("filter_page_numbers")
        text = "正文\nPage 42\n更多正文"
        result = rule.apply(text)
        assert "Page 42" not in result

    def test_preserves_number_in_text(self):
        rule = get("filter_page_numbers")
        text = "共有 12 个项目"
        result = rule.apply(text)
        assert "共有 12 个项目" in result

    def test_preserves_number_with_other_content(self):
        rule = get("filter_page_numbers")
        text = "12 个苹果"
        result = rule.apply(text)
        assert "12 个苹果" in result
