import urllib.request
import urllib.parse
import re

def test_ddg(query):
    try:
        safe_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={safe_query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        print(f"HTML length: {len(html)}")
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<div class="result__snippet"[^>]*>(.*?)</div>', html, re.DOTALL)
        print(f"Found snippets count: {len(snippets)}")
        if snippets:
            for s in snippets[:2]:
                print("-", re.sub(r'<[^>]+>', '', s).strip())
        else:
            # Let's print a part of HTML to see what's in it
            print(html[:1000])
    except Exception as e:
        print(f"Error: {e}")

test_ddg("electric cars")
