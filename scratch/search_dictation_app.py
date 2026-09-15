with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'dictation', text, re.IGNORECASE))
print(f"dictation matches in app.py: {len(matches)}")
for m in matches:
    print(text[max(0, m.start()-100):min(len(text), m.end()+150)].replace('\n', ' '))
