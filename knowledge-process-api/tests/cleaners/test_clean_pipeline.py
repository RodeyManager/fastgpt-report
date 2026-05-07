import pytest

from fastgpt_demo.cleaners.base import CleanRule
from fastgpt_demo.cleaners.registry import register, get, get_all_rules, clear
from fastgpt_demo.cleaners.pipeline import CleanPipeline


class UpperRule(CleanRule):
    name = "upper"
    description = "Convert to uppercase"
    default_enabled = True

    def apply(self, text: str, **kwargs) -> str:
        return text.upper()


class DashRule(CleanRule):
    name = "dash"
    description = "Replace spaces with dashes"
    default_enabled = False

    def apply(self, text: str, **kwargs) -> str:
        return text.replace(" ", "-")


@pytest.fixture(autouse=True)
def _clean_registry():
    clear()
    yield
    clear()


class TestCleanRule:
    def test_should_run_default_enabled(self):
        rule = UpperRule()
        assert rule.should_run({}) is True
        assert rule.should_run({"upper": True}) is True
        assert rule.should_run({"upper": False}) is False

    def test_should_run_default_disabled(self):
        rule = DashRule()
        assert rule.should_run({}) is False
        assert rule.should_run({"dash": True}) is True
        assert rule.should_run({"dash": False}) is False

    def test_apply(self):
        rule = UpperRule()
        assert rule.apply("hello") == "HELLO"


class TestRegistry:
    def test_register_and_get(self):
        rule = UpperRule()
        register(rule)
        assert get("upper") is rule

    def test_get_all_rules(self):
        r1 = UpperRule()
        r2 = DashRule()
        register(r1)
        register(r2)
        rules = get_all_rules()
        assert len(rules) == 2
        names = {r.name for r in rules}
        assert names == {"upper", "dash"}

    def test_clear(self):
        register(UpperRule())
        assert len(get_all_rules()) == 1
        clear()
        assert len(get_all_rules()) == 0

    def test_get_missing_raises(self):
        with pytest.raises(KeyError):
            get("nonexistent")


class TestCleanPipeline:
    def test_execute_with_rules(self):
        register(UpperRule())
        register(DashRule())
        pipeline = CleanPipeline()
        result = pipeline.execute("hello world", {"upper": True, "dash": True})
        assert result == "HELLO-WORLD"

    def test_execute_only_enabled(self):
        register(UpperRule())
        register(DashRule())
        pipeline = CleanPipeline()
        result = pipeline.execute("hello world", {"upper": True, "dash": False})
        assert result == "HELLO WORLD"

    def test_execute_default_options(self):
        register(UpperRule())
        register(DashRule())
        pipeline = CleanPipeline()
        result = pipeline.execute("hello world")
        assert result == "HELLO WORLD"

    def test_execute_custom_rules(self):
        pipeline = CleanPipeline(rules=[UpperRule()])
        result = pipeline.execute("hello", {"upper": True})
        assert result == "HELLO"

    def test_control_chars_replaced(self):
        pipeline = CleanPipeline(rules=[])
        result = pipeline.execute("hello\x0bworld\x1fend")
        assert result == "hello world end"
