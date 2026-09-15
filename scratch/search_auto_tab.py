with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'id="tab-content-automations"', text)]
for idx in matches:
    start = idx
    end = min(len(text), idx + 2500)
    print(f"=== AUTO TAB AT {idx} ===")
    content = text[start:end]
    content_clean = content.encode('ascii', errors='replace').decode('ascii')
    print(content_clean)
    print("-" * 60)
