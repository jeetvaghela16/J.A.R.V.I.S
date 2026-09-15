with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'research_topic|duckduckgo', text, re.IGNORECASE)]
for idx in matches:
    start = max(0, idx - 100)
    end = min(len(text), idx + 250)
    print(text[start:end].replace('\n', ' '))
    print("-" * 50)
