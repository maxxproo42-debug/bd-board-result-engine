import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

pos = text.find('curriculumCode:o')
if pos != -1:
    print('Context preceding curriculumCode:o:')
    print(text[max(0, pos-600):pos])
