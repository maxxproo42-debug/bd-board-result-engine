import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

pos = text.find('method:"POST"')
if pos != -1:
    print('Context around POST:')
    print(text[max(0, pos-300):min(len(text), pos+300)])

pos_api = text.find('/api/public')
if pos_api != -1:
    print('\nContext around /api/public:')
    print(text[max(0, pos_api-100):min(len(text), pos_api+200)])
