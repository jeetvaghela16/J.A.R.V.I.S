with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '.right-hud-tabs {' in line:
        print("Found tabs CSS context:")
        for offset in range(-2, 35):
            if idx + offset < len(lines):
                print(f"Line {idx+offset+1}: {lines[idx+offset].rstrip()}")
        break
