"""Test script for parse_comparison module."""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from parse_comparison import parse_document, SOURCE_DIR, PARSERS

# Test with first file
files = [f for f in SOURCE_DIR.iterdir() if f.is_file()]
if files:
    test_file = files[0]
    print(f'Testing with: {test_file.name}')
    for parser in ['fastgpt']:
        try:
            result = parse_document(test_file, parser)
            content = result.format_text or result.raw_text
            print(f'{parser}: OK, length={len(content)}')
            print(f'  Preview: {content[:200]}...')
        except Exception as e:
            print(f'{parser}: ERROR - {e}')
else:
    print('No files found')
