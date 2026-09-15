with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'<body', text)]
for idx in matches:
    start = idx
    end = min(len(text), idx + 2000)
    print(f"=== BODY START AT {idx} ===")
    content = text[start:end]
    # Replace non-ascii characters to avoid print errors
    content_clean = content.encode('ascii', errors='replace').decode('ascii')
    print(content_clean)
    print("-" * 60)
