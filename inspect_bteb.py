import requests
import re

r = requests.get('http://result.bteb.gov.bd/assets/result-yQpDx_Ab.js', timeout=8)
print('JS length:', len(r.text))

# Search for endpoints or paths
matches = re.findall(r'["\'](/[^"\']+)["\']', r.text)
interesting = [m for m in matches if any(k in m.lower() for k in ['result', 'search', 'student', 'api', 'hsc', 'ssc', 'diploma', 'exam'])]
print('Interesting paths:', set(interesting))

# Search for fetch calls or URLs
fetch_matches = re.findall(r'fetch\(([^)]+)\)', r.text)
print('Fetch calls:', fetch_matches[:10])

# Search for axios or baseURL
base_urls = re.findall(r'(https?://[^"\'\s<>]+)', r.text)
print('Base URLs:', set(base_urls))
