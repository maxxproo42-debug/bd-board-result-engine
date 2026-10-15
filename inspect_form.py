import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
text = r.text

# Find where rollNo or curriculumCode is in form JSX
pos = text.find('placeholder:"Roll')
if pos != -1:
    print('Context around Roll input:')
    print(text[max(0, pos-200):min(len(text), pos+400)])
else:
    pos2 = text.find('rollNo')
    print('Context around rollNo:')
    print(text[max(0, pos2-100):min(len(text), pos2+300)])
