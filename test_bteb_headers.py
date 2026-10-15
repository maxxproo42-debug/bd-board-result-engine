import requests
import base64
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)
BASE = "http://result.bteb.gov.bd"

s = requests.Session()
# Initial page get
r_home = s.get(f"{BASE}/", headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})
print("Home status:", r_home.status_code, "Cookies:", s.cookies.get_dict())

headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": BASE,
    "Referer": f"{BASE}/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r_cap = s.get(f"{BASE}/api/public/captcha", headers=headers)
c_data = r_cap.json()
token = c_data.get("token")
img_b64 = c_data.get("image", "").split(",")[-1]
raw_img = base64.b64decode(img_b64)
captcha_text = ocr.classification(raw_img)
print("Solved Captcha:", captcha_text, "Token length:", len(token))

payload = {
    "curriculumCode": "26",
    "rollNo": "208579",
    "regNo": "1502385808",
    "examYear": "2025",
    "captchaToken": token,
    "captchaAnswer": captcha_text.strip()
}

res = s.post(f"{BASE}/api/public/result", headers=headers, json=payload)
print("Result Status:", res.status_code)
print("Response text:", res.text)
