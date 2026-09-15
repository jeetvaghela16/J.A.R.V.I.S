with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'<section|<div class="[^"]*(?:container|grid|row|panel)[^"]*"', text)]
print(f"Total container matches: {len(matches)}")
for idx in matches[:25]:
    start = max(0, idx - 50)
    end = min(len(text), idx + 250)
    print(f"Match at {idx}:")
    print(text[start:end].replace('\n', ' '))
    print("-" * 50)
