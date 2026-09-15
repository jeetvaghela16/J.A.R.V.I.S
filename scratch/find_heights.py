with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find style block content
style_match = re.search(r'<style>(.*?)</style>', text, re.DOTALL)
if style_match:
    style_content = style_match.group(1)
    # Search for all definitions with height or overflow
    rules = re.findall(r'([^{]+)\{[^}]+(?:height|overflow)[^}]+}', style_content)
    for rule in rules:
        # Print the rule block
        rule_clean = rule.strip()
        rule_esc = re.escape(rule)
        m = re.search(rule_esc + r'\s*\{(.*?)\}', style_content, re.DOTALL)
        if m:
            print(f"{rule_clean}:")
            print(m.group(0).strip())
            print("-" * 50)
else:
    print("No <style> block found!")
