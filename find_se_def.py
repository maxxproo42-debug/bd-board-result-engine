import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

m = re.findall(r'(?:const|let|var|function)\s+Se\s*=?\s*([^;]+)', text)
print('Se definition:', m)
if not m:
    # search Se=
    m2 = re.findall(r'[^a-zA-Z0-9]Se=([^;]+)', text)
    print('Se= matches:', m2[:3])
