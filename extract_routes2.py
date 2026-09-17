import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'@app\.(get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)[\'"][^\)]*\)\s*(?:async\s+)?def\s+(\w+)'
matches = re.findall(pattern, content)
for method, path, func in matches:
    print(f'{method.upper():6} {path} -> {func}')