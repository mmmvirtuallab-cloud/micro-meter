# Extract CSS content from HTML
with open('micro.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

import re

# Extract CSS content
css_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
css_content = css_match.group(1).strip() if css_match else ""

# Save CSS to file
with open('style.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("CSS file created successfully")
print(f"CSS Content Length: {len(css_content)} characters")
print(f"First 200 characters of CSS:\n{css_content[:200]}...")