with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'def save_email_settings' in line:
        print(f"Line {idx+1}: {line.strip()}")
        for i in range(idx, min(len(lines), idx + 35)):
            print(f"{i+1}: {lines[i].rstrip()}")
        break
