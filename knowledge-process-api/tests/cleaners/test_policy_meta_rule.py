import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.policy_meta import PreservePolicyMetaRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(PreservePolicyMetaRule())
    yield
    clear()


class TestPreservePolicyMetaRule:
    def test_tags_policy_number(self):
        rule = get("preserve_policy_meta")
        text = "保单号：P202406010001"
        result = rule.apply(text)
        assert "[META:policy_no]" in result
        assert "P202406010001" in result
        assert "[/META]" in result

    def test_tags_contract_number(self):
        rule = get("preserve_policy_meta")
        text = "合同编号：HT20240601001"
        result = rule.apply(text)
        assert "[META:contract_no]" in result

    def test_tags_app_number(self):
        rule = get("preserve_policy_meta")
        text = "投保单号：T202406010001"
        result = rule.apply(text)
        assert "[META:app_no]" in result

    def test_tags_endorsement_number(self):
        rule = get("preserve_policy_meta")
        text = "批单号：PZ20240601001"
        result = rule.apply(text)
        assert "[META:endorsement_no]" in result

    def test_tags_insured(self):
        rule = get("preserve_policy_meta")
        text = "被保险人：张三"
        result = rule.apply(text)
        assert "[META:insured]" in result
        assert "张三" in result

    def test_tags_applicant(self):
        rule = get("preserve_policy_meta")
        text = "投保人：李四"
        result = rule.apply(text)
        assert "[META:applicant]" in result

    def test_preserves_punctuation_variant(self):
        rule = get("preserve_policy_meta")
        text = "被保险人:王五"
        result = rule.apply(text)
        assert "[META:insured]" in result

    def test_no_tag_for_irrelevant_text(self):
        rule = get("preserve_policy_meta")
        text = "这是一段普通的合同条款文本，不包含保单号信息。"
        result = rule.apply(text)
        assert "[META:" not in result

    def test_multiple_meta_in_same_text(self):
        rule = get("preserve_policy_meta")
        text = "保单号：P202406010001\n合同编号：HT20240601001\n被保人：张三"
        result = rule.apply(text)
        assert result.count("[META:") == 3
        assert result.count("[/META]") == 3
