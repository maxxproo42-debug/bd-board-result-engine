import requests
import base64
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)
BASE = "https://result.bteb.gov.bd"

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://result.bteb.gov.bd",
    "Referer": "https://result.bteb.gov.bd/"
})

# 1. Fetch fresh captcha
r_cap = s.get(f"{BASE}/api/public/captcha", timeout=5)
c_data = r_cap.json()
token = c_data.get("token")
img_b64 = c_data.get("image", "").split(",")[-1]
raw = base64.b64decode(img_b64)
cap_ans = ocr.classification(raw).strip()
print(f"Token: {token[:30]}... | Solved: {cap_ans}")

# 2. Test query
payload = {
    "curriculumCode": "26",
    "rollNo": "208579",
    "regNo": "1502385808",
    "semester": "2",
    "examYear": "2025",
    "captchaToken": token,
    "captchaAnswer": cap_ans
}

res = s.post(f"{BASE}/api/public/result", json=payload, timeout=8)
print("Status:", res.status_code)
print("Data:", res.json())
