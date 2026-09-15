with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'\.metric-card|\.metric-dial', text)]
for idx in matches:
    start = max(0, idx - 150)
    end = min(len(text), idx + 350)
    print(text[start:end])
    print("-" * 50)
