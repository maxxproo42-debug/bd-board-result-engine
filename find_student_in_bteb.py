import requests
import base64

BASE = "https://result.bteb.gov.bd"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://result.bteb.gov.bd",
    "Referer": "https://result.bteb.gov.bd/"
}

roll = "208579"
reg = "1502385808"

def solve_token(token):
    padded = token + "=" * ((4 - len(token) % 4) % 4)
    decoded_str = base64.b64decode(padded).decode('latin1')
    return decoded_str.split('.')[2]

def check(curriculum, semester, year):
    r_cap = requests.get(f"{BASE}/api/public/captcha", headers=headers, timeout=5)
    token = r_cap.json().get("token")
    cap_ans = solve_token(token)

    payload = {
        "curriculumCode": str(curriculum),
        "rollNo": str(roll),
        "regNo": str(reg),
        "semester": str(semester),
        "examYear": str(year),
        "captchaToken": token,
        "captchaAnswer": cap_ans
    }
    res = requests.post(f"{BASE}/api/public/result", headers=headers, json=payload, timeout=8)
    data = res.json()
    if data.get("data") or (data.get("code") not in ["RESULT_NOT_FOUND", "CAPTCHA_INVALID"]):
        print(f"🎉 FOUND! Cur: {curriculum}, Sem: {semester}, Year: {year}")
        print("Data:", data)
        return data
    return None

# Test common HSC / Diploma / SSC curriculums
curriculums = ['26', '24', '44', '15', '27', '77', '25', '23', '19']
years = ['2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017']

found = None
for y in years:
    print(f"Checking year {y}...")
    for c in ['26', '24', '44']: # HSC Vocational, HSC BM, HSC BM&T
        for sem in ['2', '1', '4']:
            found = check(c, sem, y)
            if found: break
        if found: break
    if found: break

if not found:
    print("Testing Diploma Engg (15)...")
    for y in years:
        for sem in ['8', '7', '6', '5', '4', '3', '2', '1']:
            found = check('15', sem, y)
            if found: break
        if found: break

if not found:
    print("Testing SSC Voc (27)...")
    for y in years:
        for sem in ['2', '1']:
            found = check('27', sem, y)
            if found: break
        if found: break

if not found:
    print("FINISHED SCAN: Student not in BTEB database under this roll/reg.")
