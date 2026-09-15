with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'use_openrouter|openrouter', text, re.IGNORECASE)]
for idx in matches:
    start = max(0, idx - 150)
    end = min(len(text), idx + 250)
    print(text[start:end].replace('\n', ' '))
    print("-" * 60)
