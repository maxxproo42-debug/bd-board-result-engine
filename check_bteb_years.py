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
    "User-Agent": "Mozilla/5.0"
}

roll = "208579"
reg = "1502385808"

# Test years
years = ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017"]
# Most common curriculums for HSC Voc / BM:
curriculums = ["24", "26", "44", "15", "27"]

found = False
for y in years:
    print(f"\n--- Checking Year {y} ---")
    for c in curriculums:
        try:
            r_cap = requests.get(f"{BASE}/captcha", headers=headers, timeout=5)
            c_data = r_cap.json()
            token = c_data.get("token")
            img_b64 = c_data.get("image", "").split(",")[-1]
            cap_ans = ocr.classification(base64.b64decode(img_b64)).strip()

            payload = {
                "curriculumCode": str(c),
                "rollNo": str(roll),
                "regNo": str(reg),
                "examYear": str(y),
                "captchaToken": token,
                "captchaAnswer": cap_ans
            }

            res = requests.post(f"{BASE}/result", headers=headers, json=payload, timeout=8)
            data = res.json()
            if data.get("data") or data.get("code") == "SUCCESS":
                print(f"!!! FOUND in Year {y}, Curriculum {c} !!!")
                print(data)
                found = True
                break
            else:
                pass
        except Exception as e:
            pass
    if found:
        break

if not found:
    print("\nNo result found in 2017-2024 on BTEB API.")
