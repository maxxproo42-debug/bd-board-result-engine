import requests
import base64
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)
BASE = "http://result.bteb.gov.bd/api/public"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def query_bteb(curriculum, roll, reg, year):
    # 1. Fetch fresh captcha
    r = requests.get(f"{BASE}/captcha", headers={"Accept": "application/json"}, timeout=5)
    c_data = r.json()
    token = c_data.get("token")
    img_b64 = c_data.get("image", "").split(",")[-1]
    raw_img = base64.b64decode(img_b64)
    captcha_text = ocr.classification(raw_img)
    print(f"Testing Curriculum {curriculum} | Solved Captcha: {captcha_text}")

    # 2. Submit result query
    # If semester is needed: try None, '', or '0'
    payload = {
        "curriculumCode": str(curriculum),
        "rollNo": str(roll).strip(),
        "regNo": str(reg).strip(),
        "examYear": str(year).strip(),
        "captchaToken": token,
        "captchaAnswer": captcha_text.strip()
    }
    res = requests.post(f"{BASE}/result", headers=headers, json=payload, timeout=8)
    print(f"Status: {res.status_code}")
    try:
        data = res.json()
        print("Response:", data)
        return data
    except Exception as e:
        print("Non-json response:", res.text[:200])
        return None

# Test user credentials across candidate curriculums
roll = "208579"
reg = "1502385808"
year = "2025"

for cur in ['26', '24', '44', '15', '27']:
    print(f"\n================ Curriculum {cur} ================")
    data = query_bteb(cur, roll, reg, year)
    if data and data.get("data"):
        print("!!! FOUND RESULT !!!")
        break
