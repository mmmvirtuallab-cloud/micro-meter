# Extract JavaScript content from HTML
with open('micro.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

import re

# Extract JavaScript content
js_match = re.search(r'<script type=\'text/javascript\'>(.*?)</script>', html_content, re.DOTALL)
js_content = js_match.group(1).strip() if js_match else ""

# Save JavaScript to file
with open('micrometer.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("JavaScript file created successfully")
print(f"JavaScript Content Length: {len(js_content)} characters")
print(f"First 300 characters of JavaScript:\n{js_content[:300]}...")