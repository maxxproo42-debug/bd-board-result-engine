import requests

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

pos = text.find("Semester ${")
if pos != -1:
    print('Context around Semester ${: ')
    print(text[max(0, pos-200):min(len(text), pos+300)])
