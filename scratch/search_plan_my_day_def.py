with open('system_tools.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'def plan_my_day', text)]
for idx in matches:
    start = idx
    end = min(len(text), idx + 1000)
    print(text[start:end].replace('\n', ' '))
