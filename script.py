# Let me extract the HTML file content and analyze its structure
with open('micro.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("HTML File Length:", len(html_content))
print("\n=== HTML STRUCTURE ANALYSIS ===")

# Extract sections
import re

# Find CSS section
css_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
css_content = css_match.group(1) if css_match else ""

# Find JavaScript section
js_match = re.search(r'<script type=\'text/javascript\'>(.*?)</script>', html_content, re.DOTALL)
js_content = js_match.group(1) if js_match else ""

# Find HTML body content
body_match = re.search(r'<body>(.*?)</body>', html_content, re.DOTALL)
body_content = body_match.group(1) if body_match else ""

print(f"CSS Content Length: {len(css_content)} characters")
print(f"JavaScript Content Length: {len(js_content)} characters")
print(f"Body Content Length: {len(body_content)} characters")

# Check for external script references
external_scripts = re.findall(r'<script src="([^"]*)"', html_content)
print(f"\nExternal Scripts Found: {external_scripts}")

# Check for image references
images = re.findall(r'src="([^"]*\.(?:png|jpg|jpeg|gif))"', html_content)
print(f"\nImages Referenced: {images}")

# Check for audio references
audio = re.findall(r'new Audio\("([^"]*)"', html_content)
print(f"\nAudio Files Referenced: {audio}")

print("\n=== FIRST 500 CHARS OF EACH SECTION ===")
print("\n--- CSS PREVIEW ---")
print(css_content[:500])

print("\n--- JAVASCRIPT PREVIEW ---")
print(js_content[:500])

print("\n--- BODY PREVIEW ---")
print(body_content[:500])