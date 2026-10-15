import requests

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

pos = text.find('mr[e]??gr')
if pos != -1:
    print('Context preceding mr[e]??gr:')
    print(text[max(0, pos-600):pos+50])
