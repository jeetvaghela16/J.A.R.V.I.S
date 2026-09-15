from html.parser import HTMLParser

class SimpleHTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        # We find matching start tag from the end
        for idx in range(len(self.tags) - 1, -1, -1):
            if self.tags[idx][0] == tag:
                self.tags.pop(idx)
                return
        # If no match, warning!
        print(f"Warning: Close tag '{tag}' at line {self.getpos()[0]} has no matching start tag.")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

parser = SimpleHTMLValidator()
parser.feed(html_content)

print(f"HTML Parsing checked. Unclosed tags: {len(parser.tags)}")
for tag, pos in parser.tags:
    # ignore void elements
    if tag not in ['meta', 'link', 'br', 'img', 'input', 'hr']:
        print(f"Unclosed tag '{tag}' opened at line {pos[0]}")
