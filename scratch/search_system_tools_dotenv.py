with open('system_tools.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'load_dotenv', text, re.IGNORECASE))
print(f"load_dotenv matches in system_tools.py: {len(matches)}")
