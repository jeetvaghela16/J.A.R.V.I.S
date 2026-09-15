with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

keywords = ['stark-diagnostics-console', 'stark-console-logs', 'logsContainer', 'addLogLine']
for kw in keywords:
    print(f"=== SEARCH FOR '{kw}' ===")
    for idx, line in enumerate(lines):
        if kw in line:
            print(f"Line {idx+1}: {line.strip()}")
    print("-" * 50)
