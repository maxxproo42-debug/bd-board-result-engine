import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

re_calls = re.findall(r're\.(get|post)\(([^)]+)\)', text)
for method, args in re_calls:
    print(method.upper(), args)
