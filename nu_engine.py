import requests
import re
import time
from urllib.parse import urljoin
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
        self._cache = {}

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
        Fetches official result from National University (results.nu.ac.bd) or Islamic Arabic University (iau.edu.bd)
        course: 'honours', 'degree', 'masters', 'fazil', or 'kamil'
        """
        course = course.lower().strip()
        roll_clean = str(roll).strip()
        reg_clean = str(reg).strip()
        year_clean = str(year).strip()
        exam_code_clean = str(exam_code).strip()

        cache_key = f"{course}:{exam_code_clean}:{roll_clean}:{reg_clean}:{year_clean}"
        if cache_key in self._cache:
            ts, cached = self._cache[cache_key]
            if time.time() - ts < 86400:
                return cached

        # Islamic Arabic University (IAU) Fazil & Kamil
        if course in ['fazil', 'kamil']:
            return self._get_iau_result(course=course, exam_code=exam_code, roll=roll, reg=reg, year=year)

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

            # Extract dynamic form action URL (handles Laravel action endpoints like /page...)
            action_m = re.search(r'<form[^>]*action="([^"]+)"', r.text)
            if action_m:
                post_url = urljoin(page_url, action_m.group(1))
            else:
                post_url = page_url

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

            res = self.session.post(post_url, data=payload, headers=post_headers, timeout=15)
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
                self._cache[cache_key] = (time.time(), parsed)
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

    def _get_iau_result(self, course='fazil', exam_code='fazil_pass_1', roll='', reg='', year='2024'):
        """
        Handles Islamic Arabic University (IAU) Fazil & Kamil examination queries
        """
        iau_portal = "http://result.iau.edu.bd"
        try:
            resp = self.session.get(iau_portal, timeout=8)
            if resp.status_code == 200 and 'result' in resp.text.lower():
                parsed = self._parse_iau_html(resp.text, course, exam_code, roll, reg, year)
                if parsed and parsed.get('success'):
                    return parsed

            return {
                "success": False,
                "is_iau": True,
                "course": course,
                "exam_code": exam_code,
                "roll": roll,
                "reg": reg,
                "year": year,
                "error": "ইসলামী আরবি বিশ্ববিদ্যালয় (IAU) সার্ভার বর্তমানে রক্ষণাবেক্ষণের কাজ চলায় ব্যস্ত রয়েছে। নিচের '📋 SMS পাঠান (16222)' বাটনে চাপ দিয়ে সাথে সাথে মোবাইলে ফলাফল জেনে নিন অথবা 'নমুনা মার্কশিট ডেমো' দেখুন।"
            }
        except Exception as e:
            return {
                "success": False,
                "is_iau": True,
                "course": course,
                "exam_code": exam_code,
                "roll": roll,
                "reg": reg,
                "year": year,
                "error": f"ইসলামী আরবি বিশ্ববিদ্যালয় (IAU) সার্ভারের সাথে সংযোগ স্থাপন করা সম্ভব হয়নি ({str(e)})। টেলিটক SMS (16222) অথবা অফিশিয়াল পোর্টালে সরাসরি চেষ্টা করুন।"
            }

    def _parse_iau_html(self, html, course, exam_code, roll, reg, year):
        data = {
            "success": True,
            "board": "ISLAMIC ARABIC UNIVERSITY, BANGLADESH",
            "exam_title": f"ISLAMIC ARABIC UNIVERSITY - {course.upper()} ({exam_code})",
            "exam_code": exam_code,
            "roll": roll,
            "reg": reg,
            "year": year,
            "name": "",
            "father": "",
            "mother": "",
            "college": "",
            "course": course.upper(),
            "session": "",
            "student_type": "Regular",
            "subject": "",
            "cgpa": "",
            "gpa": "",
            "result_status": "Passed",
            "subjects": [],
            "years_breakdown": {}
        }
        m_name = re.search(r'Student Name.*?:.*?>\s*([^<]+)<', html, re.IGNORECASE)
        if m_name: data['name'] = m_name.group(1).strip()
        m_cgpa = re.search(r'CGPA.*?:.*?>\s*([0-9\.]+)<', html, re.IGNORECASE)
        if m_cgpa: 
            data['cgpa'] = m_cgpa.group(1).strip()
            data['gpa'] = data['cgpa']
            data['result_status'] = f"Passed (CGPA: {data['cgpa']})"

        if data['name'] or data['cgpa']:
            return data
        return None

    def _parse_nu_html(self, html, course, exam_code, roll, reg, year):
        """Extracts student bio, 4-year consolidated grid, and single-year subjects from NU result page"""
        data = {
            "success": True,
            "board": "NATIONAL UNIVERSITY, BANGLADESH",
            "exam_title": f"NATIONAL UNIVERSITY - {course.upper()} ({exam_code})",
            "exam_code": exam_code,
            "roll": roll,
            "reg": reg,
            "year": year,
            "name": "",
            "father": "",
            "mother": "",
            "college": "",
            "course": course.upper(),
            "session": "",
            "student_type": "",
            "subject": "",
            "cgpa": "",
            "gpa": "",
            "result_status": "Passed",
            "subjects": [],
            "years_breakdown": {}
        }

        # Isolate result section so form elements are ignored
        pos = html.find('id="result-section"')
        sec = html[pos:] if pos != -1 else html

        # Extract Roll from result section
        m_roll = re.search(r'Examination Roll.*?<span[^>]*class="[^"]*fw-bold[^"]*"[^>]*>\s*([0-9]+)\s*</span>', sec, re.DOTALL | re.IGNORECASE)
        if m_roll:
            data['roll'] = m_roll.group(1).strip()

        # Extract Reg digits from result section
        reg_block = re.search(r'Registration No\..*?</div>\s*</div>\s*</div>', sec, re.DOTALL | re.IGNORECASE)
        if reg_block:
            digits = re.findall(r'<span[^>]*border-primary[^>]*>\s*([0-9])\s*</span>', reg_block.group(0))
            if digits:
                data['reg'] = "".join(digits)

        # Helper to extract card fields
        def get_field(label):
            pattern = rf'<span[^>]*class="text-muted[^"]*"[^>]*>\s*{label}\s*</span>\s*<span[^>]*class="fw-semibold"[^>]*>(.*?)</span>'
            match = re.search(pattern, sec, re.DOTALL | re.IGNORECASE)
            if match:
                clean = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                clean = re.sub(r'[^\x20-\x7E]+', ' - ', clean)
                clean = re.sub(r'(\s*-\s*)+', ' - ', clean)
                clean = re.sub(r'\s+', ' ', clean)
                return clean.strip(' -')
            return ""

        data['name'] = get_field('Name of Student')
        data['father'] = get_field("Father's Name")
        data['mother'] = get_field("Mother's Name")
        data['college'] = get_field('College')
        data['session'] = get_field('Session')
        data['student_type'] = get_field('Student Type')
        data['subject'] = get_field('Subject')
        if data['subject']:
            data['course'] = data['subject']

        # Extract CGPA from big badge (Consolidated 2205 / 1104)
        m_cgpa = re.search(r'CGPA.*?<div[^>]*class="fw-bold"[^>]*>\s*([0-9\.]+)\s*</div>', sec, re.DOTALL | re.IGNORECASE)
        if m_cgpa:
            data['cgpa'] = m_cgpa.group(1).strip()
            data['gpa'] = data['cgpa']

        # Extract Year GPA (Single-year e.g. 2204, 2201, 2202, 2203)
        m_ygpa = re.search(r'Year GPA:\s*([0-9\.]+)', sec, re.IGNORECASE)
        if m_ygpa:
            data['gpa'] = m_ygpa.group(1).strip()
            if not data['cgpa']:
                data['cgpa'] = data['gpa']

        # Status text
        if data['cgpa']:
            cgpa_f = float(data['cgpa']) if re.match(r'^\d+(\.\d+)?$', data['cgpa']) else 0.0
            grade_class = "First Class" if cgpa_f >= 3.00 else ("Second Class" if cgpa_f >= 2.25 else "Passed")
            data['result_status'] = f"Passed ({grade_class} | CGPA: {data['cgpa']})"
        elif data['gpa']:
            data['result_status'] = f"Passed (GPA: {data['gpa']})"

        # 4-Year Consolidated Grid (e.g. 2205, 1104)
        # Identify sub-tables that have Course Code and LG headers
        sub_tables = re.findall(r'<table[^>]*table-hover[^>]*>(.*?)</table>', sec, re.DOTALL)
        course_tables = [t for t in sub_tables if 'Course Code' in t and 'LG' in t]
        if course_tables:
            year_labels = ['First Year', 'Second Year', 'Third Year', 'Fourth Year']
            for idx, tbl in enumerate(course_tables):
                y_lbl = year_labels[idx] if idx < len(year_labels) else f"Year {idx+1}"
                rows = re.findall(r'<tr[^>]*>\s*<td>\s*([^<]+)\s*</td>\s*<td>\s*([^<]+)\s*</td>\s*</tr>', tbl)
                y_list = []
                for code, grade in rows:
                    c_clean = code.strip()
                    g_clean = grade.strip()
                    if c_clean and g_clean and 'course' not in c_clean.lower():
                        y_list.append({"code": c_clean, "grade": g_clean})
                if y_list:
                    data['years_breakdown'][y_lbl] = y_list

        # Single-Year Subject Table (e.g. 2204, 2201, 2202, 2203)
        course_rows = re.findall(
            r'<tr[^>]*>\s*<td[^>]*>\s*([0-9]{4,8})\s*</td>\s*<td[^>]*>\s*(.*?)\s*</td>\s*<td[^>]*>\s*([0-9\.]+)\s*</td>\s*<td[^>]*>\s*([A-F][\+\-]?)\s*</td>\s*</tr>',
            sec, re.DOTALL | re.IGNORECASE
        )
        for c_code, c_title, c_credit, c_grade in course_rows:
            data['subjects'].append({
                "code": c_code.strip(),
                "name": re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c_title)).strip(),
                "credit": c_credit.strip(),
                "grade": c_grade.strip()
            })

        # Fallback to old table parser if empty
        if not data['name'] and not data['subjects'] and not data['years_breakdown']:
            old_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
            for row in old_rows:
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
                    elif 'course' in txt0 or 'subject' in txt0:
                        data['subject'] = txt1
                    elif 'session' in txt0:
                        data['session'] = txt1
                    elif 'gpa' in txt0 or 'cgpa' in txt0:
                        data['cgpa'] = txt1
                        data['gpa'] = txt1

        # Check if valid data obtained
        if data['name'] or data['subjects'] or data['years_breakdown'] or data['cgpa'] or data['gpa']:
            return data

        return None

