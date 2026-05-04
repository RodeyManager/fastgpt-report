import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.clause_numbering import NormalizeClauseNumberingRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(NormalizeClauseNumberingRule())
    yield
    clear()


class TestNormalizeClauseNumberingRule:
    def test_tags_l1_article(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("第三条 保险责任\n第一项 基本条款\n申请书内容")
        assert "第三条[L1]" in result
        assert "第一项[L2]" in result

    def test_tags_l1_chapter(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("第一章 总则\n第二章 保险合同的订立")
        assert "第一章[L1]" in result
        assert "第二章[L1]" in result

    def test_tags_l2_number(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("一、基本条款\n二、附加条款")
        assert "一、[L2]" in result
        assert "二、[L2]" in result

    def test_tags_l2_paren(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("（一）基本内容\n（二）补充内容")
        assert "（一）[L2]" in result
        assert "（二）[L2]" in result

    def test_tags_l3_dotted(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("1. 条款内容\n2. 其他内容")
        assert "1. [L3]" in result

    def test_tags_l3_sub_number(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("1.1 子条款\n1.2 其他")
        assert "1.1 [L3]" in result

    def test_tags_l3_circled(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("① 第一项\n② 第二项")
        assert "①[L3]" in result

    def test_no_tag_in_body_text(self):
        rule = get("normalize_clause_numbering")
        text = "根据本合同第一条规定，保险人应当承担保险责任。"
        result = rule.apply(text)
        assert "[L" not in result

    def test_preserves_leading_whitespace(self):
        rule = get("normalize_clause_numbering")
        result = rule.apply("  一、基本条款")
        assert "一、[L2]" in result
        assert result.startswith("  ")

    def test_handles_multiple_levels(self):
        rule = get("normalize_clause_numbering")
        text = "第三条 保险责任\n一、基本保障\n1. 住院医疗\n2. 门诊医疗\n第四条 免责条款"
        result = rule.apply(text)
        lines = result.split("\n")
        assert "第三条[L1]" in lines[0]
        assert "一、[L2]" in lines[1]
        assert "1. [L3]" in lines[2]
