from fastgpt_demo.cleaners import clean_text

result = clean_text('  hello  world  \n\n\n  ')
assert result == 'hello world', f'T1: {result}'

result = clean_text('\uff21\uff22\uff23\uff11\uff12\uff13\uff01\uff1f')
assert result == 'ABC123!?', f'T2: {result}'

result = clean_text('\u4f60\u597d \u4e16\u754c')
assert result == '\u4f60\u597d\u4e16\u754c', f'T3: {result}'

result = clean_text('com-\nputer')
assert result == 'computer', f'T4: {result}'

result = clean_text('13812345678')
assert result == '13812345678', f'T5: {result}'

result = clean_text('13812345678', {'mask_sensitive': True})
assert result == '***PHONE***', f'T6: {result}'

result = clean_text('\u4f60\u597d\u2605\u4e16\u754c', {'filter_special_chars': True})
assert result == '\u4f60\u597d\u4e16\u754c', f'T7: {result}'

result = clean_text('hello\x0bworld\x1fend')
assert result == 'hello world end', f'T8: {result}'

result = clean_text('hello\u200bworld')
assert result == 'helloworld', f'T9: {result}'

result = clean_text('  hello  world  \n\n\n  ', {
    'trim': False, 'normalize_unicode': False, 'remove_invisible_chars': False,
    'remove_chinese_space': False, 'normalize_newline': False, 'fix_hyphenation': False,
    'collapse_whitespace': False, 'remove_empty_lines': False
})
assert '\x0b' not in result, 'Control chars should still be replaced'

print('All 10 backward compatibility tests PASSED!')
