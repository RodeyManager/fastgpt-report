import pytest

from fastgpt_demo.cleaners.registry import clear, register
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners.rules.table_clean import CleanTableRule
from fastgpt_demo.cleaners.rules.whitespace import TrimRule


@pytest.fixture(autouse=True)
def _setup_registry():
    clear()
    register(TrimRule())
    register(CleanTableRule())
    yield
    clear()


class TestCleanTableRule:
    def test_remove_empty_rows(self):
        text = "| Name | Age |\n| --- | --- |\n| Alice | 30 |\n|  |  |\n| Bob | 25 |"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"clean_table": True, "trim": False})
        assert "Alice" in result
        assert "Bob" in result
        assert "|  |  |" not in result

    def test_remove_empty_columns(self):
        text = "| Name |  | Age |\n| --- | --- | --- |\n| Alice |  | 30 |\n| Bob |  | 25 |"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"clean_table": True, "trim": False})
        assert "Name" in result
        assert "Age" in result
        lines = result.strip().split("\n")
        header_cells = [c.strip() for c in lines[0].split("|") if c.strip()]
        assert len(header_cells) == 2

    def test_preserve_valid_table(self):
        text = "| Name | Age |\n| --- | --- |\n| Alice | 30 |\n| Bob | 25 |"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"clean_table": True, "trim": False})
        assert "Alice" in result
        assert "Bob" in result
        assert "Name" in result

    def test_disabled_by_default(self):
        text = "| Name | Age |\n| --- | --- |\n|  |  |"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"clean_table": False, "trim": False})
        assert "|  |  |" in result

    def test_text_around_table_preserved(self):
        text = "Before text\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n\nAfter text"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"clean_table": True, "trim": False})
        assert "Before text" in result
        assert "After text" in result
        assert "| 1 | 2 |" in result

    def test_all_empty_rows_removed(self):
        text = "| A | B |\n| --- | --- |\n|  |  |\n|  |  |"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"clean_table": True, "trim": False})
        assert "|  |  |" not in result

    def test_chinese_table(self):
        text = "| \u59d3\u540d | \u5e74\u9f84 |\n| --- | --- |\n| \u5f20\u4e09 | 25 |\n|  |  |\n| \u674e\u56db | 30 |"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"clean_table": True, "trim": False})
        assert "\u5f20\u4e09" in result
        assert "\u674e\u56db" in result
        assert "|  |  |" not in result
