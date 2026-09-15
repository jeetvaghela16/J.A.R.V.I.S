with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'@app\.route\(\'\/api\/settings\/email\b|save_email', text, re.IGNORECASE)]
for idx in matches:
    start = idx
    end = min(len(text), idx + 1000)
    print(text[start:end].replace('\n', ' '))
    print("-" * 50)
