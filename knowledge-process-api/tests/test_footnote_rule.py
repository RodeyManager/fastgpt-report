import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.footnote import ProcessFootnotesRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(ProcessFootnotesRule())
    yield
    clear()


class TestProcessFootnotesRule:
    def test_removes_footnotes_by_default(self):
        rule = get("process_footnotes")
        text = "正文内容[1]\n[1] 脚注内容说明\n更多正文"
        result = rule.apply(text, footnote_action="remove")
        assert "[1] 脚注内容说明" not in result
        assert "正文内容" in result

    def test_keeps_footnotes_when_action_keep(self):
        rule = get("process_footnotes")
        text = "正文内容[1]\n[1] 脚注内容说明\n更多正文"
        result = rule.apply(text, footnote_action="keep")
        assert "[1] 脚注内容说明" in result

    def test_removes_circled_number_footnotes(self):
        rule = get("process_footnotes")
        text = "正文①内容\n①脚注说明\n更多正文"
        result = rule.apply(text, footnote_action="remove")
        assert "①脚注说明" not in result

    def test_preserves_normal_numbered_list(self):
        rule = get("process_footnotes")
        text = "1. 第一点内容\n2. 第二点内容\n正文"
        result = rule.apply(text, footnote_action="remove")
        assert "1. 第一点内容" in result

    def test_normal_text_unchanged(self):
        rule = get("process_footnotes")
        text = "普通文本没有脚注"
        result = rule.apply(text, footnote_action="remove")
        assert result == "普通文本没有脚注"
