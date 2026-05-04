import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.ocr_fix import FixOcrNumberingRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(FixOcrNumberingRule())
    yield
    clear()


class TestFixOcrNumberingRule:
    def test_fixes_l_to_1_in_clause_context(self):
        rule = get("fix_ocr_numbering")
        result = rule.apply("第 l2 条 保险责任")
        assert "第 12 条" in result

    def test_fixes_O_to_0_in_clause_context(self):
        rule = get("fix_ocr_numbering")
        result = rule.apply("第 1O 条 免责条款")
        assert "第 10 条" in result

    def test_fixes_comma_to_dunhao(self):
        rule = get("fix_ocr_numbering")
        result = rule.apply("一, 基本条款")
        assert "一、" in result

    def test_fixes_period_to_dunhao(self):
        rule = get("fix_ocr_numbering")
        result = rule.apply("一. 基本条款")
        assert "一、" in result

    def test_preserves_sub_number_with_period(self):
        rule = get("fix_ocr_numbering")
        result = rule.apply("1.1 子条款")
        assert "1.1" in result

    def test_no_fix_outside_clause_context(self):
        rule = get("fix_ocr_numbering")
        text = "保费为 l200 元，保障 O 个自然日。"
        result = rule.apply(text)
        assert "l200" in result

    def test_fixes_multiple_in_same_line(self):
        rule = get("fix_ocr_numbering")
        result = rule.apply("第 l 条 基本条款")
        assert "第 1 条" in result

    def test_preserves_normal_numbering(self):
        rule = get("fix_ocr_numbering")
        result = rule.apply("第三条 保险责任")
        assert "第三条" in result
