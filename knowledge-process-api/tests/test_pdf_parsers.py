"""Test PDF parsing with multiple parsers."""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from parse_comparison import parse_document, SOURCE_DIR

# Test with PDF file
files = [f for f in SOURCE_DIR.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
if files:
    test_file = files[0]
    print(f'Testing PDF: {test_file.name}')
    for parser in ['fastgpt', 'marker']:
        try:
            result = parse_document(test_file, parser)
            content = result.format_text or result.raw_text
            print(f'{parser}: OK, length={len(content)}')
        except Exception as e:
            print(f'{parser}: ERROR - {e}')
else:
    print('No PDF files found')
