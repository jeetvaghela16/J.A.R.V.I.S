with open('system_tools.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'def take_screenshot' in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print 40 lines after it
        for i in range(idx, min(len(lines), idx + 50)):
            print(f"{i+1}: {lines[i].rstrip()}")
        break
