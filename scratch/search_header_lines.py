with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '<header>' in line:
        print(f"Header starts at Line {idx+1}: {line.strip()}")
    if 'system-suggestions-box' in line:
        print(f"Suggestions box starts at Line {idx+1}: {line.strip()}")
