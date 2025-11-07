# Create the clean HTML file for public folder
with open('micro.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

import re

# Extract head and body content, but remove inline CSS and JS
head_match = re.search(r'<head>(.*?)</head>', html_content, re.DOTALL)
head_content = head_match.group(1) if head_match else ""

body_match = re.search(r'<body>(.*?)</body>', html_content, re.DOTALL)
body_content = body_match.group(1) if body_match else ""

# Remove inline style and script tags from head
head_content = re.sub(r'<style>.*?</style>', '', head_content, flags=re.DOTALL)
head_content = re.sub(r'<script type=\'text/javascript\'>.*?</script>', '', head_content, flags=re.DOTALL)

# Create clean HTML
clean_html = f'''<!doctype html>
<html>
<head>
    {head_content.strip()}
    <link rel="stylesheet" href="style.css">
</head>
<body>
{body_content}
    <script src="micrometer.js"></script>
</body>
</html>'''

# Save clean HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(clean_html)

print("Clean HTML file created successfully")
print(f"HTML Content Length: {len(clean_html)} characters")
print("First 500 characters of clean HTML:")
print(clean_html[:500])