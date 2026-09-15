with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function checkBackendStatus' in line:
        print(f"Line {idx+1}: {line.strip()}")
