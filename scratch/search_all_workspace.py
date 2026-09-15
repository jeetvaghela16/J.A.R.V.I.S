import os

keywords = ['Dictation Mode', 'Plan My Day', 'Smart Clipboard', 'Prepared Drafts', 'Silent Standby']
found = False

for root, dirs, files in os.walk('.'):
    # Skip venv and __pycache__
    if 'venv' in root or '__pycache__' in root or '.git' in root or '.agents' in root:
        continue
    for file in files:
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            for kw in keywords:
                if kw.lower() in content.lower():
                    print(f"Keyword '{kw}' found in {filepath}")
                    found = True
        except Exception:
            pass

if not found:
    print("None of the keywords found in workspace files.")
