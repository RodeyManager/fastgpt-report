"""
验证 clean_text() 公共 API 向后兼容性
"""

from fastgpt_demo.cleaners import clean_text


class TestBackwardCompat:
    def test_trim_and_collapse(self):
        result = clean_text('  hello  world  \n\n\n  ')
        assert result == 'hello world'

    def test_normalize_unicode(self):
        result = clean_text('\uff21\uff22\uff23\uff11\uff12\uff13\uff01\uff1f')
        assert result == 'ABC123!?'

    def test_remove_chinese_space(self):
        result = clean_text('\u4f60\u597d \u4e16\u754c')
        assert result == '\u4f60\u597d\u4e16\u754c'

    def test_fix_hyphenation(self):
        result = clean_text('com-\nputer')
        assert result == 'computer'

    def test_sensitive_disabled_by_default(self):
        result = clean_text('13812345678')
        assert result == '13812345678'

    def test_sensitive_enabled(self):
        result = clean_text('13812345678', {'mask_sensitive': True})
        assert result == '***PHONE***'

    def test_filter_special_chars(self):
        result = clean_text('\u4f60\u597d\u2605\u4e16\u754c', {'filter_special_chars': True})
        assert result == '\u4f60\u597d\u4e16\u754c'

    def test_control_chars_replaced(self):
        result = clean_text('hello\x0bworld\x1fend')
        assert result == 'hello world end'

    def test_remove_invisible_chars(self):
        result = clean_text('hello\u200bworld')
        assert result == 'helloworld'

    def test_all_rules_disabled_still_replaces_control_chars(self):
        result = clean_text('  hello  world  \n\n\n  ', {
            'trim': False, 'normalize_unicode': False, 'remove_invisible_chars': False,
            'remove_chinese_space': False, 'normalize_newline': False, 'fix_hyphenation': False,
            'collapse_whitespace': False, 'remove_empty_lines': False
        })
        assert '\x0b' not in result
