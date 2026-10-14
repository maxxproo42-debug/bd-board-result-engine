import urllib.request, urllib.parse, urllib.error, http.cookiejar, re, ssl, time, json, hashlib, base64, io
from collections import Counter
from PIL import Image

try:
    import ddddocr
    HAS_DDDDOCR = True
except ImportError:
    HAS_DDDDOCR = False

class DinajpurUnifiedEngine:
    """
    Unified All-Years (2015 - 2026) Engine for Dinajpur Education Board:
    - Primary: Dinajpur Direct Portal (2023 - 2026) with automated challenge & math captcha bypass
    - Archive: Central eBoard Gateway (2015 - 2024) with automated SHA-256 robot bypass and AI captcha solver
    """

    CHAR_MAP = {
        'o': '0', 'O': '0', 'D': '0', 'Q': '0', 'd': '0',
        'l': '1', 'I': '1', 'i': '1', '(': '1', ')': '1', '|': '1', '[': '1', '/': '1', 'J': '1', 'j': '1',
        'z': '2', 'Z': '2',
        'E': '3', 'e': '3',
        'A': '4', 'h': '4', 'H': '4', 'M': '4',
        's': '5', 'S': '5',
        'b': '6', 'G': '6',
        'T': '7', 't': '7', 'F': '7',
        'B': '8', '&': '8',
        'g': '9', 'q': '9', 'p': '9', 'P': '9'
    }

    EXAM_MAP_DINAJPUR = {
        ('HSC', '2026'): {'exam_id': '', 'archive': '', 'title': 'HSC EXAMINATION 2026'},
        ('HSC', '2025'): {'exam_id': '3', 'archive': '1', 'title': 'HSC EXAMINATION 2025'},
        ('SSC', '2026'): {'exam_id': '', 'archive': '', 'title': 'SSC EXAMINATION 2026'},
        ('SSC', '2025'): {'exam_id': '2', 'archive': '1', 'title': 'SSC EXAMINATION 2025'},
        ('SSC', '2024'): {'exam_id': '4', 'archive': '1', 'title': 'SSC EXAMINATION 2024'},
        ('SSC', '2023'): {'exam_id': '5', 'archive': '1', 'title': 'SSC EXAMINATION 2023'},
    }

    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

        # AI Captcha Solver
        self._ocr = None
        if HAS_DDDDOCR:
            try:
                self._ocr = ddddocr.DdddOcr(show_ad=False)
            except Exception as e:
                print(f"[OCR Init Warning]: {e}")

        # Dinajpur Direct Session
        self.dinajpur_base = "https://results.dinajpurboard.gov.bd"
        self.dinajpur_cj = http.cookiejar.CookieJar()
        self.dinajpur_opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.dinajpur_cj),
            urllib.request.HTTPSHandler(context=self.ctx)
        )
        self.dinajpur_opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'),
            ('Accept-Language', 'en-US,en;q=0.9,bn;q=0.8'),
            ('Referer', self.dinajpur_base)
        ]
        self._dinajpur_ready = False

        # Central eBoard Archive Session
        self.eboard_base = "https://eboardresults.com"
        self.eboard_cj = http.cookiejar.CookieJar()
        self.eboard_opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.eboard_cj),
            urllib.request.HTTPSHandler(context=self.ctx)
        )
        self.eboard_opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'),
            ('Referer', f"{self.eboard_base}/v2/home")
        ]
        self._eboard_ready = False

        # Asynchronously pre-warm sessions in background thread
        import threading
        threading.Thread(target=self._prewarm_sessions, daemon=True).start()

    def _prewarm_sessions(self):
        try:
            self._ensure_dinajpur_session()
        except Exception:
            pass
        try:
            self._bypass_eboard_robot()
        except Exception:
            pass

    # =========================================================================
    # Dinajpur Direct Portal Engine (2023 - 2026)
    # =========================================================================
    def _ensure_dinajpur_session(self):
        try:
            req = urllib.request.Request(f"{self.dinajpur_base}/results")
            res = self.dinajpur_opener.open(req, timeout=8)
            html = res.read().decode('utf-8', errors='ignore')

            if 'challenge-page' in html or 'result-check' in html:
                token_m = re.search(r'name="_token"\s+value="([^"]+)"', html)
                c_token_m = re.search(r'name="challenge_token"\s+value="([^"]+)"', html)
                if not token_m or not c_token_m:
                    return False
                
                token = token_m.group(1)
                c_token = c_token_m.group(1)
                matches = re.findall(r'value="(\d+)"[^>]*>[\s\n]*<span aria-hidden="true">([^<]+)</span>', html)
                if not matches:
                    return False

                counts = Counter([sym.strip() for val, sym in matches])
                diff_sym = [sym for sym, count in counts.items() if count == 1][0]
                ans = [val for val, sym in matches if sym.strip() == diff_sym][0]

                post_data = urllib.parse.urlencode({
                    '_token': token,
                    'challenge_token': c_token,
                    'answer': ans
                }).encode('utf-8')

                req2 = urllib.request.Request(f"{self.dinajpur_base}/result-check", data=post_data)
                self.dinajpur_opener.open(req2, timeout=8)
            self._dinajpur_ready = True
            return True
        except Exception as e:
            print(f"[Dinajpur Session Error]: {e}")
            return False

    def _get_dinajpur_direct_result(self, roll_no, regi_no="", exam="HSC", year="2025"):
        roll_clean = str(roll_no).strip()
        reg_clean = str(regi_no).strip() if regi_no else ""
        exam_key = (exam.upper(), str(year))

        cfg = self.EXAM_MAP_DINAJPUR.get(exam_key)
        if not cfg:
            return {"success": False, "not_in_direct": True}

        exam_id = cfg['exam_id']
        archive = cfg['archive']
        exam_title = cfg.get('title', f'{exam} {year}')

        for attempt in range(2):
            try:
                if not self._dinajpur_ready and attempt == 0:
                    self._ensure_dinajpur_session()

                search_url = f"{self.dinajpur_base}/search/student"
                params = []
                if archive:
                    params.append(f"archive={archive}")
                if exam_id:
                    params.append(f"exam_id={exam_id}")
                if params:
                    search_url += "?" + "&".join(params)

                req = urllib.request.Request(search_url)
                res = self.dinajpur_opener.open(req, timeout=10)
                html = res.read().decode('utf-8', errors='ignore')

                if 'challenge-page' in html or 'result-check' in html:
                    self._ensure_dinajpur_session()
                    res = self.dinajpur_opener.open(req, timeout=10)
                    html = res.read().decode('utf-8', errors='ignore')

                token_m = re.search(r'name="_token"\s+value="([^"]+)"', html)
                if not token_m:
                    if attempt == 0:
                        self._ensure_dinajpur_session()
                        continue
                    return {"success": False, "error": "সার্ভার টোকেন পাওয়া যায়নি, অনুগ্রহ করে পুনরায় চেষ্টা করুন।"}
                token = token_m.group(1)

                cap_match = re.search(r'class="board-captcha-q"[^>]*>(\d+)\s*([\+\-\*])\s*(\d+)\s*=\s*\?</span>', html)
                if not cap_match:
                    return {"success": False, "error": "ক্যাপচা সমাধান সম্ভব হয়নি।"}
                n1, op, n2 = cap_match.group(1), cap_match.group(2), cap_match.group(3)
                captcha_ans = str(eval(f"{n1} {op} {n2}"))

                post_data_dict = {
                    '_token': token,
                    'roll_no': roll_clean,
                    'regi_no': reg_clean,
                    'captcha': captcha_ans,
                    'submit': '1'
                }
                if archive:
                    post_data_dict['archive'] = archive
                if exam_id:
                    post_data_dict['exam_id'] = exam_id

                post_data = urllib.parse.urlencode(post_data_dict).encode('utf-8')
                req_post = urllib.request.Request(f"{self.dinajpur_base}/search/student", data=post_data)
                res_post = self.dinajpur_opener.open(req_post, timeout=12)
                out_html = res_post.read().decode('utf-8', errors='ignore')

                if "No Result Found" in out_html or "not found" in out_html.lower():
                    return {
                        "success": False,
                        "error": f"রোল {roll_clean} এর কোনো রেজাল্ট {year} সালের {exam} পরীক্ষায় পাওয়া যায়নি।"
                    }

                data = {
                    "success": True,
                    "source": "dinajpur_direct",
                    "exam_title": f"RESULT OF {exam_title}",
                    "exam": exam,
                    "year": str(year)
                }
                pairs = [
                    ('roll', r'Roll No</b></td>\s*<td><b>([^<]+)</b>'),
                    ('reg', r'Registration No</b></td>\s*<td>([^<]+)</td>'),
                    ('name', r'Name of Student:</b></td>\s*<td[^>]*><b>([^<]+)</b>'),
                    ('father', r'Father\'s Name</b></td>\s*<td[^>]*>([^<]+)</td>'),
                    ('mother', r'Mother\'s Name</b></td>\s*<td[^>]*>([^<]+)</td>'),
                    ('institute', r'Name of Institute</b></td>\s*<td[^>]*>([^<]+)</td>'),
                    ('board', r'Board</b></td>\s*<td>([^<]+)</td>'),
                    ('session', r'Session</b></td>\s*<td>([^<]+)</td>'),
                    ('group', r'Group</b></td>\s*<td>([^<]+)</td>'),
                    ('type', r'Type:</b></td>\s*<td>([^<]+)</td>'),
                    ('gpa', r'Result</b></td>\s*<td[^>]*><b>(?:GPA=)?([^<]+)</b>'),
                    ('total_marks', r'TOTAL MARK</b></td>\s*<td[^>]*><b>([^<]+)</b>')
                ]
                for k, pat in pairs:
                    m = re.search(pat, out_html, re.I)
                    data[k] = m.group(1).strip() if m else ''

                subjects = []
                sub_rows = re.findall(r'<tr[^>]*>\s*<td class="c">(\d+)</td>\s*<td class="l">(.*?)</td>\s*<td class="c">.*?<span class="grade-letter">([^<]+)</span>(?:<span class="grade-mod">([^<]*)</span>)?', out_html)
                for code, raw_name, g_letter, g_mod in sub_rows:
                    grade = g_letter + (g_mod if g_mod else '')
                    clean_name = re.sub(r'<[^>]+>', ' ', raw_name).strip()
                    clean_name = re.sub(r'\s+', ' ', clean_name)
                    subjects.append({'code': code.strip(), 'name': clean_name, 'grade': grade.strip()})
                data['subjects'] = subjects

                if not data['roll']: data['roll'] = roll_clean
                if not data['reg'] and reg_clean: data['reg'] = reg_clean
                return data

            except urllib.error.HTTPError as err:
                if err.code == 404:
                    return {
                        "success": False,
                        "error": f"রোল {roll_clean} এর কোনো রেজাল্ট {year} সালের {exam} পরীক্ষায় পাওয়া যায়নি। রোল নম্বর বা পরীক্ষার সাল সঠিক আছে কি না মিলিয়ে নিন।"
                    }
                elif err.code == 429:
                    time.sleep(2)
                    continue
                else:
                    return {"success": False, "error": f"বোর্ড সার্ভার ত্রুটি (HTTP {err.code})"}
            except Exception as e:
                if attempt == 0:
                    time.sleep(1)
                    continue
                return {"success": False, "error": f"সার্ভার সংযোগে ত্রুটি: {str(e)}"}
        return {"success": False, "error": "রেজাল্ট আনতে ব্যর্থ হয়েছে।"}

    # =========================================================================
    # Central eBoard Archive Engine (2015 - 2022)
    # =========================================================================
    def _bypass_eboard_robot(self):
        try:
            res = self.eboard_opener.open(f'{self.eboard_base}/v2/home', timeout=10)
            html = res.read().decode('utf-8', errors='ignore')

            m = re.search(r'var challenge\s*=\s*({[^;]+});', html)
            if m:
                c = json.loads(m.group(1))
                proof = f"browser-proof:{c['seed']}:{c['salt']}".encode('utf-8')
                h = hashlib.sha256(proof).hexdigest()
                ans = 'hash:' + h

                verify_payload = json.dumps({'token': c['token'], 'answer': ans}).encode('utf-8')
                req_v = urllib.request.Request(
                    f'{self.eboard_base}/_challenge-verify',
                    data=verify_payload,
                    headers={'Content-Type': 'application/json'}
                )
                res_v = self.eboard_opener.open(req_v, timeout=10)
                v_data = json.loads(res_v.read().decode())
                if v_data.get('ok'):
                    self.eboard_opener.open(f'{self.eboard_base}/v2/home', timeout=10)
                    self._eboard_ready = True
                    return True
            else:
                self._eboard_ready = True
                return True
        except Exception as e:
            print(f"[eBoard Challenge Error]: {e}")
            return False

    def _solve_archive_captcha(self, img_bytes):
        """AI Automated 4-digit numeric solver with consensus majority voting across crop ratios."""
        if not self._ocr:
            return ""
        try:
            im = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            w, h = im.size
            candidates = []
            # Multi-pass crop to remove bottom interference waves
            for crop_ratio in [0.72, 0.76, 0.80, 0.84, 1.0]:
                crop_h = int(h * crop_ratio)
                c_im = im.crop((0, 0, w, crop_h)) if crop_h < h else im
                buf = io.BytesIO()
                c_im.save(buf, format='PNG')
                raw = self._ocr.classification(buf.getvalue())
                digits = ''
                for ch in raw:
                    if ch.isdigit():
                        digits += ch
                    elif ch in self.CHAR_MAP:
                        digits += self.CHAR_MAP[ch]
                if len(digits) == 4:
                    candidates.append(digits)
            if candidates:
                counts = Counter(candidates)
                return counts.most_common(1)[0][0]
        except Exception as e:
            print(f"[AI Captcha Solver Error]: {e}")
        return ""

    def get_archive_captcha_base64(self):
        """Returns fresh 4-digit security captcha image in base64 format for archive searches."""
        if not self._eboard_ready:
            self._bypass_eboard_robot()
        try:
            res = self.eboard_opener.open(f'{self.eboard_base}/v2/captcha', timeout=8)
            img_bytes = res.read()
            return base64.b64encode(img_bytes).decode('ascii'), img_bytes
        except Exception as e:
            self._bypass_eboard_robot()
            res = self.eboard_opener.open(f'{self.eboard_base}/v2/captcha', timeout=8)
            img_bytes = res.read()
            return base64.b64encode(img_bytes).decode('ascii'), img_bytes

    def _get_eboard_archive_result(self, roll, reg="", exam="hsc", year="2018", board="dinajpur", captcha=""):
        if not self._eboard_ready:
            self._bypass_eboard_robot()

        board_clean = str(board).strip().lower() if board else "dinajpur"
        exam_code = exam.lower()
        if 'hsc' in exam_code or 'alim' in exam_code: exam_code = 'hsc'
        elif 'ssc' in exam_code or 'dakhil' in exam_code: exam_code = 'ssc'
        elif 'jsc' in exam_code or 'jdc' in exam_code: exam_code = 'jsc'

        roll_clean = str(roll).strip()
        reg_clean = str(reg).strip()
        manual_code = str(captcha).strip() if captcha else ""

        # Auto-Bypass Loop: if no manual captcha provided or if manual captcha fails, try AI solver
        max_attempts = 1 if manual_code else 7
        last_error = ""

        for attempt in range(max_attempts):
            if manual_code and attempt == 0:
                cur_captcha = manual_code
            else:
                # Fetch fresh captcha and solve with AI
                try:
                    c_res = self.eboard_opener.open(f'{self.eboard_base}/v2/captcha', timeout=8)
                    raw_img = c_res.read()
                    cur_captcha = self._solve_archive_captcha(raw_img)
                    if not cur_captcha:
                        continue
                except Exception:
                    continue

            p_data = urllib.parse.urlencode({
                'board': board_clean,
                'exam': exam_code,
                'year': str(year),
                'result_type': '1',
                'roll': roll_clean,
                'reg': reg_clean,
                'captcha': cur_captcha
            }).encode('utf-8')

            try:
                req = urllib.request.Request(f'{self.eboard_base}/v2/getres', data=p_data)
                res = self.eboard_opener.open(req, timeout=12)
                raw_resp = json.loads(res.read().decode())
            except Exception as e:
                last_error = str(e)
                continue

            if raw_resp.get('status') == 0:
                # 🌟 SUCCESS! Result fetched!
                res_data = raw_resp.get('res', {})
                gpa_str = res_data.get('res_detail', '')
                if gpa_str.startswith('P'): gpa_str = gpa_str.replace('P', 'PASSED').strip()

                subjects = []
                disp_details = res_data.get('display_details', '')
                if disp_details:
                    for item in disp_details.split(','):
                        if ':' in item:
                            parts = item.split(':')
                            code = parts[0].strip()
                            g_info = parts[1].split('=')[-1].strip()
                            subjects.append({'code': code, 'name': f'Subject {code}', 'grade': g_info})

                board_display = "BANGLADESH MADRASAH EDUCATION BOARD, DHAKA" if board_clean == "madrasah" else f"BOARD OF INTERMEDIATE & SECONDARY EDUCATION, {board_clean.upper()}"
                exam_display = exam.upper()
                if board_clean == "madrasah":
                    if exam_code == 'hsc': exam_display = 'ALIM'
                    elif exam_code == 'ssc': exam_display = 'DAKHIL'
                    elif exam_code == 'jsc': exam_display = 'JDC'

                return {
                    "success": True,
                    "source": "eboard_archive",
                    "exam_title": f"RESULT OF {exam_display} EXAMINATION {year}",
                    "exam": exam_display,
                    "year": str(year),
                    "roll": res_data.get('roll_no', roll_clean),
                    "reg": res_data.get('regno', reg_clean or '[HIDDEN]'),
                    "name": res_data.get('name', 'N/A'),
                    "father": res_data.get('fname', 'N/A'),
                    "mother": res_data.get('mname', 'N/A'),
                    "institute": res_data.get('inst_name', res_data.get('eiin', 'N/A')),
                    "board": board_display,
                    "session": res_data.get('session', 'N/A'),
                    "group": res_data.get('stud_group', 'N/A'),
                    "type": res_data.get('stud_type', 'N/A'),
                    "gpa": gpa_str.replace('GPA=', '').strip(),
                    "total_marks": "",
                    "subjects": subjects
                }

            msg = raw_resp.get('msg', '')
            msg_upper = msg.upper()

            # If the error is NOT captcha-related (e.g. invalid reg, result not found), STOP immediately!
            if "SECURITY" not in msg_upper and "CAPTCHA" not in msg_upper and "KEY" not in msg_upper:
                board_label = "মাদ্রাসা" if board_clean == "madrasah" else "দিনাজপুর"
                if "REGISTRATION" in msg_upper:
                    bn_err = f"{board_label} বোর্ডের সেন্ট্রাল আর্কাইভে একক রেজাল্ট দেখতে রোল {roll_clean} এর সাথে সঠিক রেজিস্ট্রেশন নম্বর আবশ্যক।"
                elif "NOT FOUND" in msg_upper or "INVALID" in msg_upper:
                    bn_err = f"{board_label} বোর্ডের {year} সালের {exam.upper()} পরীক্ষায় রোল {roll_clean} বা রেজিস্ট্রেশন নম্বরের কোনো রেজাল্ট মেলেনি। অনুগ্রহ করে রোল, রেজিস্ট্রেশন ও সাল সঠিক আছে কি না মিলিয়ে নিন।"
                else:
                    bn_err = f"আর্কাইভ রেজাল্ট পাওয়া যায়নি: {msg}"
                return {
                    "success": False,
                    "need_captcha": False,
                    "error": bn_err
                }

            # If it failed due to captcha and we have retries left, continue loop!
            last_error = msg

        # If all AI auto-bypass attempts failed: prompt with fresh captcha image
        new_b64, new_raw = self.get_archive_captcha_base64()
        suggested = self._solve_archive_captcha(new_raw)
        return {
            "success": False,
            "need_captcha": True,
            "captcha_img": new_b64,
            "suggested_captcha": suggested,
            "error": "ক্যাপচা কোডটি অটোমেটিক মেলেনি। অনুগ্রহ করে নিচে প্রদর্শিত কোডটি যাচাই করে পুনরায় সাবমিট করুন।"
        }

    # =========================================================================
    # Universal Public Router
    # =========================================================================
    def get_student_result(self, roll_no, regi_no="", exam="HSC", year="2025", board="dinajpur", captcha=""):
        board_clean = str(board).strip().lower() if board else "dinajpur"
        y = int(year) if str(year).isdigit() else 2025
        roll_clean = str(roll_no).strip()
        reg_clean = str(regi_no).strip() if regi_no else ""
        exam_upper = exam.upper()

        # If board is Dinajpur and directly supported on Dinajpur Direct Portal:
        if board_clean == "dinajpur":
            is_direct = (exam_upper, str(year)) in self.EXAM_MAP_DINAJPUR
            if is_direct and not captcha:
                res = self._get_dinajpur_direct_result(roll_clean, reg_clean, exam, year)
                if res.get('success'):
                    return res

        # For Central eBoard Archive (all years for Madrasah, and 2015-2024 for Dinajpur):
        # Registration number is strictly required by the central government archive:
        if not reg_clean:
            board_label = "মাদ্রাসা" if board_clean == "madrasah" else "দিনাজপুর"
            return {
                "success": False,
                "need_captcha": False,
                "need_reg": True,
                "error": f"📌 বাংলাদেশ শিক্ষা বোর্ডের নিয়মানুযায়ী {board_label} বোর্ডের {year} সালের সেন্ট্রাল আর্কাইভ থেকে একক রেজাল্ট দেখতে রোল নম্বরের সাথে ১০ সংখ্যার রেজিস্ট্রেশন নম্বর দেওয়া আবশ্যক। অনুগ্রহ করে আপনার রেজিস্ট্রেশন নম্বরটি লিখুন।\n\n(নোট: আপনার রেজিস্ট্রেশন নম্বর জানা না থাকলে 'পুরো প্রতিষ্ঠানের রেজাল্ট (EIIN)' ট্যাব থেকে প্রতিষ্ঠানের রেজাল্ট দেখতে পারেন।)"
            }

        # 🌟 Seamless Auto-Bypass: Call _get_eboard_archive_result directly!
        return self._get_eboard_archive_result(roll_clean, reg_clean, exam, year, board=board_clean, captcha=captcha)

    def get_institute_result(self, eiin_no, exam="HSC", year="2025"):
        # Institute results for Dinajpur board
        eiin_clean = str(eiin_no).strip()
        exam_key = (exam.upper(), str(year))
        cfg = self.EXAM_MAP_DINAJPUR.get(exam_key, {'exam_id': '3', 'archive': '1', 'title': f'{exam} {year}'})
        exam_id = cfg['exam_id']

        try:
            if not self._dinajpur_ready:
                self._ensure_dinajpur_session()

            url = f"{self.dinajpur_base}/search/institute?verify={eiin_clean}"
            if exam_id:
                url += f"&exam_id={exam_id}"

            req = urllib.request.Request(url)
            res = self.dinajpur_opener.open(req, timeout=15)
            html = res.read().decode('utf-8', errors='ignore')

            if "No Result Found" in html or "not found" in html.lower():
                return {"success": False, "error": f"EIIN: {eiin_clean} এর কোনো প্রতিষ্ঠান {year} সালের {exam} পরীক্ষায় পাওয়া যায়নি।"}

            data = {
                "success": True,
                "eiin": eiin_clean,
                "exam_title": f"INSTITUTE RESULT · {cfg.get('title', exam)}",
                "exam": exam,
                "year": str(year)
            }
            m_inst = re.search(r'Institute</td>\s*<td[^>]*><b>([^<]+)</b>', html)
            data['institute'] = m_inst.group(1).strip() if m_inst else ''
            
            m_thana = re.search(r'Thana/Upazilla</td>\s*<td[^>]*>([^<]+)</td>', html)
            data['thana'] = m_thana.group(1).strip() if m_thana else ''

            for key, pat in [('gpa5', r'GPA 5\.00</td>\s*<td><b>([^<]+)</b>'),
                             ('appeared', r'Appeared</td>\s*<td><b>([^<]+)</b>'),
                             ('passed', r'Passed</td>\s*<td><b>([^<]+)</b>'),
                             ('pass_pct', r'Pass %</td>\s*<td><b>([^<]+)</b>')]:
                m = re.search(pat, html)
                data[key] = m.group(1).strip() if m else ''

            sections = {}
            sec_blocks = re.findall(r'<div class="result-section">(.*?)(?=<div class="result-section"|<div class="nav-row|\Z)', html, re.DOTALL)
            for blk in sec_blocks:
                title_m = re.search(r'<div class="section-title">\s*<span>:\s*([^:]+)\s*:</span>', blk)
                title = title_m.group(1).strip() if title_m else 'General'
                items = re.findall(r'<span class="rest-item">([^<,]+)', blk)
                sections[title] = items
            data['groups'] = sections
            return data
        except Exception as e:
            return {"success": False, "error": f"প্রতিষ্ঠান রেজাল্ট অনুসন্ধানে ত্রুটি: {str(e)}"}
