import requests

BASE = "http://result.bteb.gov.bd/api/public"
headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

print("1. Fetching curriculums...")
try:
    r = requests.get(f"{BASE}/curriculums", headers=headers, timeout=5)
    print("Status:", r.status_code)
    print(r.json())
except Exception as e:
    print("Curriculums error:", e)

print("\n2. Fetching captcha...")
try:
    r2 = requests.get(f"{BASE}/captcha", headers=headers, timeout=5)
    print("Status:", r2.status_code)
    print(r2.json())
except Exception as e:
    print("Captcha error:", e)
