import requests
import base64
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)
BASE = "https://result.bteb.gov.bd/api/public"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://result.bteb.gov.bd",
    "Referer": "https://result.bteb.gov.bd/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

roll = "208579"
reg = "1502385808"
year = "2025"

# First get all active curriculums
r_curr = requests.get(f"{BASE}/curriculums", headers=headers, timeout=5)
curriculums = r_curr.json()
print(f"Total curriculums: {len(curriculums)}")

for c in curriculums:
    code = c.get("curriculumCode")
    name = c.get("curriculumName")

    # Only test relevant curriculums
    # HSC BM, HSC Voc, BM Tech, Diploma, SSC Voc, etc.
    if code not in ['24', '26', '44', '15', '25', '27', '77', '19', '23', '72', '74']:
        continue

    # Get fresh captcha
    try:
        r_cap = requests.get(f"{BASE}/captcha", headers=headers, timeout=5)
        c_data = r_cap.json()
        token = c_data.get("token")
        img_b64 = c_data.get("image", "").split(",")[-1]
        cap_ans = ocr.classification(base64.b64decode(img_b64)).strip()

        payload = {
            "curriculumCode": str(code),
            "rollNo": str(roll),
            "regNo": str(reg),
            "examYear": str(year),
            "captchaToken": token,
            "captchaAnswer": cap_ans
        }

        res = requests.post(f"{BASE}/result", headers=headers, json=payload, timeout=8)
        data = res.json()
        print(f"[{code}] {name} -> {data.get('code')}: {data.get('message')}")
        if data.get("data"):
            print("Found DATA:", data.get("data"))
            with open("bteb_found_result.json", "w", encoding="utf-8") as f_out:
                import json
                json.dump(data, f_out, indent=2)
            break
    except Exception as e:
        print(f"[{code}] Error: {e}")
