import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.toc_filter import FilterTocRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(FilterTocRule())
    yield
    clear()


class TestFilterTocRule:
    def test_removes_numeric_toc(self):
        rule = get("filter_toc")
        text = "1.1 概述 .... 12\n1.2 背景 .... 15\n1.3 方法 .... 20\n正文内容"
        result = rule.apply(text)
        assert "1.1 概述" not in result
        assert "正文内容" in result

    def test_removes_chinese_chapter_toc(self):
        rule = get("filter_toc")
        text = "第一章 引言\n第二章 方法\n第三章 结果\n正文内容"
        result = rule.apply(text)
        assert "第一章" not in result
        assert "正文内容" in result

    def test_preserves_short_numbered_list(self):
        rule = get("filter_toc")
        text = "1. 第一点\n2. 第二点\n正文内容"
        result = rule.apply(text)
        assert "1. 第一点" in result

    def test_preserves_normal_text(self):
        rule = get("filter_toc")
        text = "这是一段普通文本\n没有目录格式"
        result = rule.apply(text)
        assert result == text

    def test_toc_needs_three_consecutive_lines(self):
        rule = get("filter_toc")
        text = "1.1 概述 .... 12\n1.2 背景 .... 15\n正文内容"
        result = rule.apply(text)
        assert "1.1 概述" in result

    def test_removes_appendix_toc(self):
        rule = get("filter_toc")
        text = "附录A 数据表\n附录B 代码\n附录C 参考文献\n正文内容"
        result = rule.apply(text)
        assert "附录A" not in result
        assert "正文内容" in result
