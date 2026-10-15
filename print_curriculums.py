import requests

BASE = "http://result.bteb.gov.bd/api/public"
headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(f"{BASE}/curriculums", headers=headers, timeout=5)
data = r.json()
print("Curriculums count:", len(data))
for c in data:
    print(c)
