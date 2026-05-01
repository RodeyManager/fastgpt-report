import pytest

from fastgpt_demo.parsers.html_parser import parse


class TestHtmlParserNoiseRemoval:
    def test_removes_script_tags(self):
        html = b"<html><body><script>alert('x')</script><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "alert" not in result.format_text
        assert "content" in result.format_text

    def test_removes_nav_tags(self):
        html = b"<html><body><nav>menu</nav><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "menu" not in result.format_text
        assert "content" in result.format_text

    def test_removes_footer_tags(self):
        html = b"<html><body><footer>copyright</footer><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "copyright" not in result.format_text
        assert "content" in result.format_text

    def test_identifies_article_content(self):
        html = b"<html><body><nav>menu</nav><article><p>main content</p></article></body></html>"
        result = parse(html, remove_noise=True)
        assert "main content" in result.format_text
        assert "menu" not in result.format_text

    def test_no_noise_removal_when_disabled(self):
        html = b"<html><body><nav>menu</nav><p>content</p></body></html>"
        result = parse(html, remove_noise=False)
        assert "menu" in result.format_text

    def test_preserves_raw_text(self):
        html = b"<html><body><nav>menu</nav><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "menu" in result.raw_text
