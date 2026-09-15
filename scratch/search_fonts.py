with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Fonts in new index.html:")
for m in re.finditer(r'<link[^>]*fonts\.googleapis[^>]*>', text):
    print(m.group(0))
