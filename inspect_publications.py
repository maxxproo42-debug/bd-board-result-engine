import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

# Search for curriculumCode or active-publications
pos = text.find('active-publications')
if pos != -1:
    print('Context around active-publications:')
    print(text[max(0, pos-200):min(len(text), pos+300)])
