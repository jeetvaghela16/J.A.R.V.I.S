with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find styling of chat bubbles, assistant responses, etc.
for match in re.finditer(r'class="[^"]*message[^"]*"|id="[^"]*message[^"]*"|class="[^"]*bubble[^"]*"|class="[^"]*chat[^"]*"', text):
    start = max(0, match.start() - 100)
    end = min(len(text), match.end() + 200)
    print(f"--- MATCH AT {match.start()} ---")
    print(text[start:end])
