import requests
import base64
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)
BASE = "http://result.bteb.gov.bd"

s = requests.Session()
r_cap = s.get(f"{BASE}/api/public/captcha", headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
print("Captcha status:", r_cap.status_code)
c_data = r_cap.json()
token = c_data.get("token")
img_b64 = c_data.get("image", "").split(",")[-1]
captcha_text = ocr.classification(base64.b64decode(img_b64))
print("Solved Captcha:", captcha_text)

payload = {
    "curriculumCode": "26",
    "rollNo": "208579",
    "regNo": "1502385808",
    "examYear": "2025",
    "captchaToken": token,
    "captchaAnswer": captcha_text.strip()
}

# Try POST without extra origin first
res = s.post(f"{BASE}/api/public/result", json=payload, headers={
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
})
print("Result status:", res.status_code)
print("Result text:", repr(res.text[:300]))
