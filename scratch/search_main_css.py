with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'main\s*\{', text)]
for idx in matches:
    start = max(0, idx - 100)
    end = min(len(text), idx + 400)
    print(f"=== MATCH AT {idx} ===")
    content = text[start:end]
    content_clean = content.encode('ascii', errors='replace').decode('ascii')
    print(content_clean)
    print("-" * 60)
