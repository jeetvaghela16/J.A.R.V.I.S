with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
keywords = ['stark-diagnostics-console', 'stark-console-logs', 'logsContainer', 'addLogLine']
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), text)]
    print(f"=== SEARCH FOR '{kw}' ({len(matches)} matches) ===")
    for idx in matches:
        start = max(0, idx - 150)
        end = min(len(text), idx + 250)
        print(f"Context near index {idx}:")
        print(text[start:end])
        print("-" * 50)
