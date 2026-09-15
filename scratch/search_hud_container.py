with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'\.hud-container|\.main-layout|\.dashboard-grid|body\s*\{', text)]
for idx in matches:
    start = max(0, idx - 100)
    end = min(len(text), idx + 350)
    print(f"=== MATCH AT {idx} ===")
    print(text[start:end])
    print("-" * 60)
