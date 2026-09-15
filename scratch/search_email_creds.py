with open('system_tools.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '_get_email_credentials' in line:
        print(f"Line {idx+1}: {line.strip()}")
        for i in range(idx, min(len(lines), idx + 20)):
            print(f"{i+1}: {lines[i].rstrip()}")
        break
