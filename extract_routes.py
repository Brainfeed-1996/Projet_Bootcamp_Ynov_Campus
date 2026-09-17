import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

routes = re.findall(r'@app\.(get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)[\'"]', content)
for method, path in routes:
    print(f'{method.upper():6} {path}')