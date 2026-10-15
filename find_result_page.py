import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

pos = text.find('getItem("bteb_result_data")')
if pos != -1:
    print('Context around getItem:')
    print(text[max(0, pos-100):min(len(text), pos+800)])
