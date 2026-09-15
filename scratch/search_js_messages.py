with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find function declarations or elements related to adding messages to the chat log
matches = [m.start() for m in re.finditer(r'appendMessage|chat-log|chat-bubble|addMessage', text)]
for idx in matches:
    start = max(0, idx - 200)
    end = min(len(text), idx + 400)
    print(f"=== MATCH AT {idx} ===")
    print(text[start:end])
    print("-" * 60)
