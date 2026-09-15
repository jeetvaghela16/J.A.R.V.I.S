with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find styling blocks containing chat-log or chat-bubble
rules = ['.chat-log', '.chat-bubble', '.sender', 'stark-diagnostics-console', 'stark-console-logs']
for rule in rules:
    print(f"=== SEARCH FOR {rule} ===")
    matches = [m.start() for m in re.finditer(re.escape(rule), text)]
    for idx in matches:
        start = max(0, idx - 150)
        end = min(len(text), idx + 250)
        print(f"Context near index {idx}:")
        print(text[start:end])
        print("-" * 50)
