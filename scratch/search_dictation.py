with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = [m.start() for m in re.finditer(r'dictat|typing|type|voice-to-text', html, re.IGNORECASE)]
print(f"Total matches in templates/index.html: {len(matches)}")
for idx in matches[:10]:
    start = max(0, idx - 100)
    end = min(len(html), idx + 250)
    print(html[start:end].replace('\n', ' '))
    print("-" * 50)
