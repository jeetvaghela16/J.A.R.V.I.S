with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
match = re.search(r'<style>', text)
if match:
    idx = match.start()
    start = idx
    end = min(len(text), idx + 2000)
    print(text[start:end])
else:
    print("Style tag not found")
