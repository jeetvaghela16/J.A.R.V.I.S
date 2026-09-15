with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'<div class="system-stats">', text)]
for idx in matches:
    start = idx
    end = min(len(text), idx + 4000)
    print(f"=== SYSTEM-STATS AT {idx} ===")
    content = text[start:end]
    content_clean = content.encode('ascii', errors='replace').decode('ascii')
    print(content_clean)
    print("-" * 60)
