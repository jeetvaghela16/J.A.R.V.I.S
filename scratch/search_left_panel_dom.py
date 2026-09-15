with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'SYSTEM METRICS' in line:
        print("Found SYSTEM METRICS context:")
        for offset in range(-5, 45):
            if idx + offset < len(lines):
                print(f"Line {idx+offset+1}: {lines[idx+offset].rstrip()}")
        break
