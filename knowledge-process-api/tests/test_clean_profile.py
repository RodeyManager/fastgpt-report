import pytest

from fastgpt_demo.cleaners.profiles.base import CleanProfile
from fastgpt_demo.cleaners.profiles.registry import (
    register_profile, get_profile, get_profile_for_file, clear_profiles,
)


@pytest.fixture(autouse=True)
def _clean():
    from fastgpt_demo.cleaners.profiles import _reset_loaded
    clear_profiles()
    _reset_loaded()
    yield
    clear_profiles()
    _reset_loaded()


class TestCleanProfile:
    def test_to_options_dict(self):
        p = CleanProfile(
            name="test",
            description="test profile",
            rules={"trim": True, "filter_toc": True},
            params={"watermark_min_repeat": 3},
        )
        d = p.to_options_dict()
        assert d["trim"] is True
        assert d["filter_toc"] is True
        assert d["watermark_min_repeat"] == 3

    def test_register_and_get(self):
        p = CleanProfile(name="test", description="test", rules={}, params={})
        register_profile(p)
        assert get_profile("test") is p

    def test_get_profile_for_file_pdf(self):
        p = CleanProfile(name="pdf_academic", description="test", rules={}, params={})
        register_profile(p)
        assert get_profile_for_file("paper.pdf").name == "pdf_academic"

    def test_get_profile_for_file_html(self):
        p = CleanProfile(name="web_content", description="test", rules={}, params={})
        register_profile(p)
        assert get_profile_for_file("page.html").name == "web_content"

    def test_get_profile_for_file_unknown(self):
        assert get_profile_for_file("unknown.xyz") is None

    def test_get_missing_profile(self):
        assert get_profile("nonexistent") is None


class TestBuiltinProfiles:
    def test_default_profile_exists(self):
        from fastgpt_demo.cleaners.profiles import _load_builtins
        _load_builtins()
        p = get_profile("default")
        assert p is not None
        assert p.name == "default"

    def test_pdf_academic_profile(self):
        from fastgpt_demo.cleaners.profiles import _load_builtins
        _load_builtins()
        p = get_profile("pdf_academic")
        assert p is not None
        opts = p.to_options_dict()
        assert opts.get("filter_toc") is True
        assert opts.get("filter_page_numbers") is True

    def test_web_content_profile(self):
        from fastgpt_demo.cleaners.profiles import _load_builtins
        _load_builtins()
        p = get_profile("web_content")
        assert p is not None
        opts = p.to_options_dict()
        assert opts.get("filter_html_noise") is True

    def test_all_profiles_load(self):
        from fastgpt_demo.cleaners.profiles import _load_builtins, get_all_profiles
        _load_builtins()
        names = {p.name for p in get_all_profiles()}
        assert "default" in names
        assert "pdf_academic" in names
        assert "pdf_business" in names
        assert "docx_report" in names
        assert "table_data" in names
        assert "legal" in names
        assert "web_content" in names
