import requests

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

pos = text.find("examination year")
if pos != -1:
    print('Context preceding examination year:')
    print(text[max(0, pos-600):pos])
