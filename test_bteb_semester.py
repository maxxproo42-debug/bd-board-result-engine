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

# Test curriculums 26, 24, 44, 25, 27
# Test semester '2' (Class 12/Final), '1' (Class 11)
# Test years 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017
found = False

for c in ['24', '26', '44', '25', '27']:
    for sem in ['2', '1']:
        for y in ['2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017']:
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
                    "semester": str(sem),
                    "examYear": str(y),
                    "captchaToken": token,
                    "captchaAnswer": cap_ans
                }

                res = requests.post(f"{BASE}/result", headers=headers, json=payload, timeout=8)
                data = res.json()
                if data.get("data") or data.get("code") == "SUCCESS":
                    print(f"\n🎉🎉🎉 FOUND RESULT! 🎉🎉🎉")
                    print(f"Curriculum: {c}, Semester: {sem}, Year: {y}")
                    print("Data:", data)
                    with open("bteb_real_student.json", "w", encoding="utf-8") as f_out:
                        import json
                        json.dump(data, f_out, indent=2)
                    found = True
                    break
                else:
                    if data.get("code") != "RESULT_NOT_FOUND":
                        print(f"[{c}-{sem}-{y}] {data}")
            except Exception as e:
                pass
        if found:
            break
    if found:
        break

if not found:
    print("\nChecked all curriculums with semester 1 and 2 for 2017-2025.")
