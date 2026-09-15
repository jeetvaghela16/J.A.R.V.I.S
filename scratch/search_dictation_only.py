with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
d_matches = list(re.finditer(r'dictation', html, re.IGNORECASE))
clip_matches = list(re.finditer(r'clipboard', html, re.IGNORECASE))
print(f"dictation matches in HTML: {len(d_matches)}")
print(f"clipboard matches in HTML: {len(clip_matches)}")
