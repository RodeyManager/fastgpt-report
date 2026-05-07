import pytest

from fastgpt_demo.cleaners.registry import clear, register
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners.rules.watermark import FilterWatermarkRule
from fastgpt_demo.cleaners.rules.whitespace import TrimRule


@pytest.fixture(autouse=True)
def _setup_registry():
    clear()
    register(TrimRule())
    register(FilterWatermarkRule())
    yield
    clear()


class TestFilterWatermarkRule:
    def test_repeat_short_line_removed(self):
        text = "RepeatLine\nHello world\nRepeatLine\nSome content\nRepeatLine"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"filter_watermark": True, "trim": False})
        assert "RepeatLine" not in result
        assert "Hello world" in result
        assert "Some content" in result

    def test_keyword_match_removed(self):
        text = "\u673a\u5bc6\nThis is secret\nNormal line"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"filter_watermark": True, "trim": False})
        assert "\u673a\u5bc6" not in result
        assert "Normal line" in result

    def test_custom_keywords(self):
        text = "MY CUSTOM WATERMARK\nHello\nMY CUSTOM WATERMARK"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {
            "filter_watermark": True,
            "watermark_keywords": ["MY CUSTOM WATERMARK"],
            "trim": False,
        })
        assert "MY CUSTOM WATERMARK" not in result
        assert "Hello" in result

    def test_disabled_by_default(self):
        text = "RepeatLine\nHello\nRepeatLine"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"filter_watermark": False, "trim": False})
        assert "RepeatLine" in result

    def test_long_line_not_removed(self):
        text = "This is a very long line that exceeds the max line length\nHello"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {
            "filter_watermark": True,
            "watermark_min_repeat": 2,
            "watermark_max_line_length": 30,
            "trim": False,
        })
        assert "This is a very long line" in result

    def test_keyword_in_long_line_not_removed(self):
        text = "This document is about watermark detection methods\nHello"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {
            "filter_watermark": True,
            "watermark_max_line_length": 30,
            "trim": False,
        })
        assert "This document is about" in result

    def test_case_insensitive_keyword(self):
        text = "confidential\nHello\nconfidential"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"filter_watermark": True, "trim": False})
        assert "confidential" not in result

    def test_min_repeat_configurable(self):
        text = "ShortRepeat\nLine A\nShortRepeat\nLine B\nShortRepeat"
        pipeline = CleanPipeline()
        result_4 = pipeline.execute(text, {
            "filter_watermark": True,
            "watermark_min_repeat": 4,
            "trim": False,
        })
        assert "ShortRepeat" in result_4

        result_2 = pipeline.execute(text, {
            "filter_watermark": True,
            "watermark_min_repeat": 2,
            "trim": False,
        })
        assert "ShortRepeat" not in result_2

    def test_keyword_short_line_always_removed(self):
        text = "DRAFT\nHello world"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"filter_watermark": True, "trim": False})
        assert "DRAFT" not in result
        assert "Hello world" in result
