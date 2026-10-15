import requests
from dinajpur_engine import DinajpurUnifiedEngine

engine = DinajpurUnifiedEngine()
roll = "208579"
reg = "1502385808"

# Check all boards and exams
boards = ['tec', 'dinajpur', 'dhaka', 'madrasah', 'rajshahi', 'chittagong', 'comilla', 'jessore', 'barisal', 'sylhet', 'mymensingh']
exams = ['hsc', 'ssc', 'jsc']
years = ['2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017']

found = False
for b in boards:
    for y in ['2025', '2024', '2023', '2022']:
        for e in ['hsc', 'ssc']:
            try:
                res = engine._query_archive_api(exam=e, year=y, board=b, roll=roll, reg=reg, max_valid_attempts=1)
                if res.get('success'):
                    print(f"!!! FOUND RESULT in {b} | {e} | {y} !!!")
                    print(res)
                    found = True
                    break
                else:
                    err = res.get('error', '')
                    if 'BTEB.GOV.BD' in err or 'সরাসরি তাদের নিজস্ব সরকারি' in err:
                        print(f"[{b}-{e}-{y}] BTEB Redirect returned: {err}")
                    elif 'কোনো রেজাল্ট মেলেনি' in err:
                        pass
                    else:
                        print(f"[{b}-{e}-{y}] {err[:80]}")
            except Exception as ex:
                pass
        if found:
            break
    if found:
        break
