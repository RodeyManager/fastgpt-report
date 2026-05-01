import pytest

from fastgpt_demo.cleaners.registry import clear, register
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners.rules.deduplication import DeduplicateParagraphsRule
from fastgpt_demo.cleaners.rules.whitespace import TrimRule


@pytest.fixture(autouse=True)
def _setup_registry():
    clear()
    register(TrimRule())
    register(DeduplicateParagraphsRule())
    yield
    clear()


class TestDeduplicateParagraphsRule:
    def test_exact_dedup(self):
        text = "First paragraph\n\nSecond paragraph\n\nFirst paragraph"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"deduplicate_paragraphs": True, "trim": False})
        assert result.count("First paragraph") == 1
        assert "Second paragraph" in result

    def test_no_dedup_when_disabled(self):
        text = "First paragraph\n\nFirst paragraph"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"deduplicate_paragraphs": False, "trim": False})
        assert result.count("First paragraph") == 2

    def test_different_paragraphs_kept(self):
        text = "Paragraph A\n\nParagraph B\n\nParagraph C"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"deduplicate_paragraphs": True, "trim": False})
        assert "Paragraph A" in result
        assert "Paragraph B" in result
        assert "Paragraph C" in result

    def test_fuzzy_dedup(self):
        text = "The quick brown fox jumps over the lazy dog\n\nThe quick brown fox jumped over the lazy dogs"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {
            "deduplicate_paragraphs": True,
            "dedup_fuzzy": True,
            "dedup_fuzzy_threshold": 0.9,
            "trim": False,
        })
        assert result.count("quick brown fox") == 1

    def test_fuzzy_dedup_threshold(self):
        text = "Hello world this is a test\n\nHello world this is different"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {
            "deduplicate_paragraphs": True,
            "dedup_fuzzy": True,
            "dedup_fuzzy_threshold": 0.95,
            "trim": False,
        })
        assert "Hello world this is a test" in result
        assert "Hello world this is different" in result

    def test_empty_paragraphs_preserved(self):
        text = "First\n\n\n\nSecond\n\nFirst"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"deduplicate_paragraphs": True, "trim": False})
        assert "Second" in result

    def test_chinese_dedup(self):
        text = "\u8fd9\u662f\u7b2c\u4e00\u6bb5\n\n\u8fd9\u662f\u7b2c\u4e8c\u6bb5\n\n\u8fd9\u662f\u7b2c\u4e00\u6bb5"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"deduplicate_paragraphs": True, "trim": False})
        assert result.count("\u8fd9\u662f\u7b2c\u4e00\u6bb5") == 1
        assert "\u8fd9\u662f\u7b2c\u4e8c\u6bb5" in result

    def test_multiple_duplicates(self):
        text = "A\n\nB\n\nA\n\nC\n\nA"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"deduplicate_paragraphs": True, "trim": False})
        assert result.count("A") == 1
        assert "B" in result
        assert "C" in result
