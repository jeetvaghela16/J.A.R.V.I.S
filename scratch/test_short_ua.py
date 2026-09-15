import urllib.request
import urllib.parse
import re

def test_ddg_short_ua():
    try:
        safe_query = urllib.parse.quote_plus("electric cars")
        url = f"https://html.duckduckgo.com/html/?q={safe_query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
        print(f"HTML length: {len(html)}")
        
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<div class="result__snippet"[^>]*>(.*?)</div>', html, re.DOTALL)
        print(f"Snippets: {len(snippets)}")
        if not snippets:
            print(html[:2000])
    except Exception as e:
        print(f"Failed with error: {e}")

test_ddg_short_ua()
