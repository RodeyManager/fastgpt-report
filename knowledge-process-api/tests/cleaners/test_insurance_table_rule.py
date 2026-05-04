import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.insurance_table import CleanInsuranceTableRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(CleanInsuranceTableRule())
    yield
    clear()


class TestCleanInsuranceTableRule:
    def test_preserves_annotation_row(self):
        rule = get("clean_insurance_table")
        text = "| 项目 | 费率 |\n| --- | --- |\n| 意外 | 0.1% |\n注：以上费率为每千元保额"
        result = rule.apply(text)
        assert "注：" in result

    def test_preserves_explanation_row(self):
        rule = get("clean_insurance_table")
        text = "说明：费率会根据年龄调整"
        result = rule.apply(text)
        assert "说明：" in result

    def test_preserves_summary_row(self):
        rule = get("clean_insurance_table")
        text = "| 项目 | 金额 |\n| --- | --- |\n| 合计 | 10000 |"
        result = rule.apply(text)
        assert "合计" in result

    def test_preserves_total_row(self):
        rule = get("clean_insurance_table")
        text = "| 总计 | 5000 元 |"
        result = rule.apply(text)
        assert "总计" in result

    def test_preserves_beizhu_row(self):
        rule = get("clean_insurance_table")
        text = "备注：本表格数据仅供参考"
        result = rule.apply(text)
        assert "备注：" in result

    def test_preserves_normal_text(self):
        rule = get("clean_insurance_table")
        text = "普通文本内容"
        result = rule.apply(text)
        assert "普通文本内容" in result

    def test_handles_mixed_content(self):
        rule = get("clean_insurance_table")
        text = "| 项目 | 费率 |\n| --- | --- |\n| 意外 | 0.1% |\n注：以上费率为每千元保额\n| 合计 | 0.1% |"
        result = rule.apply(text)
        assert "注：" in result
        assert "合计" in result
