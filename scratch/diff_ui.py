with open('templates/index.html', 'r', encoding='utf-8') as f:
    new_html = f.read()

with open('templates/index_backup.html', 'r', encoding='utf-8') as f:
    old_html = f.read()

import re

# Compare chat panel css and structures
# Let's search for "chat-log" or "chat-bubble" or "message" in both and print differences
def find_block(text, keyword):
    matches = [m.start() for m in re.finditer(re.escape(keyword), text)]
    results = []
    for idx in matches:
        start = max(0, idx - 150)
        end = min(len(text), idx + 250)
        results.append(text[start:end])
    return results

print("=== NEW CHAT-LOG ===")
for b in find_block(new_html, "chat-log")[:2]:
    print(b)
    print("-" * 40)

print("=== OLD CHAT-LOG ===")
for b in find_block(old_html, "chat-log")[:2]:
    print(b)
    print("-" * 40)

print("=== NEW CHAT-BUBBLE ===")
for b in find_block(new_html, "chat-bubble")[:2]:
    print(b)
    print("-" * 40)

print("=== OLD CHAT-BUBBLE ===")
for b in find_block(old_html, "chat-bubble")[:2]:
    print(b)
    print("-" * 40)
