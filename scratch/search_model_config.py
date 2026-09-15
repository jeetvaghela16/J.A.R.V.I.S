with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'provider|model|gemini', text, re.IGNORECASE)]
print(f"Total matches: {len(matches)}")
for idx in matches[:15]:
    start = max(0, idx - 100)
    end = min(len(text), idx + 250)
    print(text[start:end].replace('\n', ' '))
    print("-" * 50)
