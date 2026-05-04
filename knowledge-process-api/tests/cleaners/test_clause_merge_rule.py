import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.clause_merge import MergeBrokenClausesRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(MergeBrokenClausesRule())
    yield
    clear()


class TestMergeBrokenClausesRule:
    def test_merges_broken_clause_across_newline(self):
        rule = get("merge_broken_clauses")
        text = "第三十二条 保险责任的免除\n因下列原因造成被保险人身故的，保险人不承\n担给付保险金的责任。"
        result = rule.apply(text)
        assert "保险人不承担给付保险金的责任。" in result
        assert "保险人不承\n担" not in result

    def test_preserves_broken_clause_with_punctuation(self):
        rule = get("merge_broken_clauses")
        text = "第三十三条 保险期间\n本合同的保险期间为一年。\n自本合同生效之日起计算。"
        result = rule.apply(text)
        assert "保险期间为一年。" in result

    def test_preserves_clause_boundary(self):
        rule = get("merge_broken_clauses")
        text = "第三十二条 免责条款\n内容A\n第三十三条 保险期间\n内容B"
        result = rule.apply(text)
        assert "第三十二条" in result
        assert "第三十三条" in result
        assert result.count("内容A") >= 1
        assert result.count("内容B") >= 1

    def test_preserves_empty_lines_outside_clause(self):
        rule = get("merge_broken_clauses")
        text = "普通文本\n\n第三条 保险责任\n保险责任内容。"
        result = rule.apply(text)
        assert result.startswith("普通文本\n\n")

    def test_merges_multiple_continuation_lines(self):
        rule = get("merge_broken_clauses")
        text = "第三条 保险责任\n因下列\n原因造成\n被保险人身故的。"
        result = rule.apply(text)
        assert "因下列原因造成被保险人身故的。" in result

    def test_preserves_sentence_end_punctuation(self):
        rule = get("merge_broken_clauses")
        text = "第一条 基本条款\n本条款内容完整。\n第二条 其他条款"
        result = rule.apply(text)
        assert "内容完整。" in result
        assert "第二条" in result

    def test_no_merge_without_clause_start(self):
        rule = get("merge_broken_clauses")
        text = "这是一段\n被截断的\n普通文本。"
        result = rule.apply(text)
        assert "\n" in result
