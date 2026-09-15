with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

import re
features = ['Dictation Mode', 'clipboard', 'plan my day', 'Prepared Drafts', 'Ctrl + Shift + J', 'hotkey', 'next track']
for feat in features:
    print(f"=== SEARCH FOR '{feat}' ===")
    html_matches = list(re.finditer(re.escape(feat), html, re.IGNORECASE))
    app_matches = list(re.finditer(re.escape(feat), app, re.IGNORECASE))
    print(f"index.html matches: {len(html_matches)}")
    print(f"app.py matches: {len(app_matches)}")
    for m in html_matches[:2]:
        print(f"index.html: {html[max(0, m.start()-50):min(len(html), m.end()+100)].strip()}")
    for m in app_matches[:2]:
        print(f"app.py: {app[max(0, m.start()-50):min(len(app), m.end()+100)].strip()}")
    print("-" * 50)
