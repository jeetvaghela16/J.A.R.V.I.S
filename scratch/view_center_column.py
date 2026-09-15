with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'reactor-core|stark-diagnostics-console', text)]
for idx in matches:
    start = max(0, idx - 800)
    end = min(len(text), idx + 800)
    print(f"=== MATCH AT {idx} ===")
    print(text[start:end])
    print("-" * 60)
