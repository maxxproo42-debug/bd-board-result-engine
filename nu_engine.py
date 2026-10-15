import requests
import re
from html.parser import HTMLParser

class NuResultEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        })
        self.base_url = "https://results.nu.ac.bd"

    def _solve_math_captcha(self, html):
        """Extracts and solves NU's math captcha (e.g. 15 + 12 =)"""
        m = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)\s*=', html)
        if m:
            n1, op, n2 = m.groups()
            n1, n2 = int(n1), int(n2)
            if op == '+': return str(n1 + n2)
            if op == '-': return str(n1 - n2)
            if op == '*': return str(n1 * n2)
        return "0"

    def get_result(self, course='honours', exam_code='2204', roll='', reg='', year='2022'):
        """
        Fetches official result from National University (results.nu.ac.bd)
        course: 'honours', 'degree', or 'masters'
        """
        course = course.lower().strip()
        endpoint = f"/{course}" if course in ['honours', 'degree', 'masters'] else '/honours'
        page_url = f"{self.base_url}{endpoint}"

        try:
            # 1. Fetch form and CSRF token
            r = self.session.get(page_url, timeout=12)
            if r.status_code != 200:
                return {"success": False, "error": f"জাতীয় বিশ্ববিদ্যালয় সার্ভার রেসপন্স করছে না (Code: {r.status_code})"}

            token_m = re.search(r'name="_token" value="([^"]+)"', r.text)
            if not token_m:
                return {"success": False, "error": "জাতীয় বিশ্ববিদ্যালয় সিকিউরিটি টোকেন পাওয়া যায়নি।"}
            csrf_token = token_m.group(1)

            # 2. Solve Math Captcha
            captcha_ans = self._solve_math_captcha(r.text)

            # 3. Submit Search Query
            payload = {
                '_token': csrf_token,
                'examination_name': str(exam_code).strip(),
                'year': str(year).strip(),
                'examination_roll': str(roll).strip(),
                'registration_no': str(reg).strip(),
                'captcha': str(captcha_ans).strip()
            }

            post_headers = {
                'Referer': page_url,
                'Origin': self.base_url
            }

            res = self.session.post(page_url, data=payload, headers=post_headers, timeout=15)
            html = res.text

            # 4. Check for alerts / errors
            alerts = re.findall(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
            clean_alerts = [re.sub(r'<[^>]+>', '', a).strip() for a in alerts if a.strip()]
            for alert in clean_alerts:
                if 'no result' in alert.lower() or 'not found' in alert.lower():
                    return {
                        "success": False,
                        "error": "জাতীয় বিশ্ববিদ্যালয়ের ডাটাবেসে এই রোল ও রেজিস্ট্রেশনের কোনো ফলাফল পাওয়া যায়নি। অনুগ্রহ করে পরীক্ষার সাল, রোল ও রেজিস্ট্রেশন নম্বর সঠিকভাবে যাচাই করুন।"
                    }

            # 5. Parse Student Information & Subject Results
            parsed = self._parse_nu_html(html, course, exam_code, roll, reg, year)
            if parsed and parsed.get('success'):
                return parsed

            if clean_alerts:
                return {"success": False, "error": clean_alerts[0]}

            return {
                "success": False,
                "error": "জাতীয় বিশ্ববিদ্যালয় সার্ভারে এই রোল ও রেজিস্ট্রেশনের কোনো তথ্য মেলেনি। দয়া করে সাল ও রোল নিশ্চিত করুন।"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"জাতীয় বিশ্ববিদ্যালয় সার্ভারে সংযোগ বিঘ্নিত হয়েছে: {str(e)}"
            }

    def _parse_nu_html(self, html, course, exam_code, roll, reg, year):
        """Extracts student bio and subject grades from NU result page using regex"""
        # Look for table rows
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
        if not rows:
            return None

        data = {
            "success": True,
            "board": "NATIONAL UNIVERSITY",
            "exam_title": f"NATIONAL UNIVERSITY - {course.upper()}",
            "roll": roll,
            "reg": reg,
            "year": year,
            "name": "",
            "father": "",
            "mother": "",
            "college": "",
            "course": "",
            "session": "",
            "gpa": "0.00",
            "result_status": "Passed",
            "subjects": []
        }

        for row in rows:
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            td_texts = [re.sub(r'<[^>]+>', '', t).strip() for t in tds]
            if len(td_texts) >= 2:
                txt0 = td_texts[0].lower()
                txt1 = td_texts[1]
                if 'student name' in txt0 or 'name of examinee' in txt0:
                    data['name'] = txt1
                elif "father's name" in txt0:
                    data['father'] = txt1
                elif "mother's name" in txt0:
                    data['mother'] = txt1
                elif 'college' in txt0 or 'institution' in txt0:
                    data['college'] = txt1
                elif 'course' in txt0 or 'subject' in txt0 or 'degree' in txt0:
                    data['course'] = txt1
                elif 'session' in txt0:
                    data['session'] = txt1
                elif 'gpa' in txt0 or 'cgpa' in txt0 or 'result' in txt0:
                    data['result_status'] = txt1
                    gpa_m = re.search(r'(\d+\.\d+)', txt1)
                    if gpa_m:
                        data['gpa'] = gpa_m.group(1)

            # Course codes / grade table row (usually 3+ columns)
            if len(td_texts) >= 3:
                c_code = td_texts[0]
                c_title = td_texts[1]
                c_grade = td_texts[2]
                if re.match(r'^\d{4,7}$', c_code) and c_title:
                    data['subjects'].append({
                        "code": c_code,
                        "name": c_title,
                        "grade": c_grade
                    })

        # Check if we got valid details
        if data['name'] or data['subjects'] or data['gpa'] != "0.00" or 'passed' in data['result_status'].lower() or 'promoted' in data['result_status'].lower():
            return data

        return None
