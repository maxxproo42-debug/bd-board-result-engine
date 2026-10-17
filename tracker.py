import sqlite3
import os
import re
import datetime
import urllib.request
import json
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'visitors.db')
GEO_CACHE = {}
REVERSE_GEO_CACHE = {}

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                path TEXT,
                method TEXT,
                device TEXT,
                phone_model TEXT,
                os TEXT,
                browser TEXT,
                country TEXT,
                region TEXT,
                city TEXT,
                exact_location TEXT,
                location_source TEXT,
                isp TEXT,
                gps_lat REAL,
                gps_lon REAL,
                gps_accuracy REAL,
                gpu TEXT,
                screen TEXT,
                ram TEXT,
                user_agent TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Ensure new columns exist for existing db
        existing_cols = [col[1] for col in c.execute("PRAGMA table_info(visitors)").fetchall()]
        cols_to_add = {
            'phone_model': 'TEXT',
            'region': 'TEXT',
            'city': 'TEXT',
            'exact_location': 'TEXT',
            'location_source': 'TEXT',
            'isp': 'TEXT',
            'gps_lat': 'REAL',
            'gps_lon': 'REAL',
            'gps_accuracy': 'REAL',
            'gpu': 'TEXT',
            'screen': 'TEXT',
            'ram': 'TEXT'
        }
        for col_name, col_type in cols_to_add.items():
            if col_name not in existing_cols:
                c.execute(f"ALTER TABLE visitors ADD COLUMN {col_name} {col_type}")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Tracker DB Init Error]: {e}")

def reverse_geocode(lat, lon):
    try:
        cache_key = f"{round(float(lat), 3)},{round(float(lon), 3)}"
        if cache_key in REVERSE_GEO_CACHE:
            return REVERSE_GEO_CACHE[cache_key]
        
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'DinajpurEduTracker/2.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            addr = data.get('address', {})
            parts = []
            for k in ['suburb', 'neighbourhood', 'village', 'town', 'city', 'county', 'state_district', 'state']:
                val = addr.get(k)
                if val and val not in parts:
                    parts.append(val)
            if parts:
                clean_name = ', '.join(parts)
                REVERSE_GEO_CACHE[cache_key] = clean_name
                return clean_name
            if data.get('display_name'):
                clean_name = ', '.join(data.get('display_name').split(',')[:4])
                REVERSE_GEO_CACHE[cache_key] = clean_name
                return clean_name
    except Exception:
        pass
    return None

def format_brand_model(model_str):
    if not model_str:
        return "Smartphone"
    m_clean = str(model_str).strip(' "')
    upper_m = m_clean.upper()
    if 'IPHONE' in upper_m or 'IPAD' in upper_m or 'APPLE' in upper_m:
        return m_clean
    if 'WINDOWS' in upper_m or 'MAC' in upper_m or 'LINUX' in upper_m or 'DESKTOP' in upper_m or 'PC' in upper_m:
        return m_clean
    if upper_m.startswith('SM-'):
        return f"Samsung Galaxy ({m_clean})"
    elif upper_m.startswith(('REDMI', 'POCO', 'MI ', '220', '210', '230')):
        return f"Xiaomi / Redmi ({m_clean})"
    elif upper_m.startswith('RMX'):
        return f"Realme ({m_clean})"
    elif upper_m.startswith(('CPH', 'OPPO')):
        return f"OPPO ({m_clean})"
    elif upper_m.startswith(('V2', 'VIVO')):
        return f"Vivo ({m_clean})"
    elif upper_m.startswith('X') or 'INFINIX' in upper_m:
        return f"Infinix ({m_clean})"
    elif 'TECNO' in upper_m:
        return f"Tecno ({m_clean})"
    elif 'ONEPLUS' in upper_m:
        return f"OnePlus ({m_clean})"
    elif 'PIXEL' in upper_m:
        return f"Google Pixel ({m_clean})"
    elif 'WALTON' in upper_m:
        return f"Walton Primo ({m_clean})"
    elif 'SYMPHONY' in upper_m:
        return f"Symphony ({m_clean})"
    return f"Android ({m_clean})"

def extract_phone_and_os(ua, ch_model=None):
    if not ua:
        return "Unknown Device", "Unknown", "Unknown"
    
    ua_lower = ua.lower()
    
    # Check Bots first
    if any(b in ua_lower for b in ['bot', 'crawler', 'spider', 'curl', 'python', 'wget', 'slurp']):
        return "Automated Bot", "Bot / Crawler", "Bot"
    
    # If Client Hint header provides explicit phone model
    if ch_model and ch_model.strip(' "'):
        model_clean = ch_model.strip(' "')
        return format_brand_model(model_clean), "Mobile", "Android/Chrome"

    # Apple Devices
    if "iphone" in ua_lower:
        m = re.search(r'iPhone OS ([\d_]+)', ua)
        ios_ver = m.group(1).replace('_', '.') if m else ''
        phone_name = f"Apple iPhone (iOS {ios_ver})" if ios_ver else "Apple iPhone"
        return phone_name, "iPhone", "iOS"
        
    if "ipad" in ua_lower:
        return "Apple iPad", "Tablet", "iPadOS"
        
    # Android Phones - parse exact model from User Agent
    if "android" in ua_lower:
        m = re.search(r'Android\s+[\d.]+;\s*([^;)]+?)(?:\s+Build|[;)])', ua, re.IGNORECASE)
        model_str = m.group(1).strip() if m else ""
        model_str = re.sub(r'^(wv|mobile)\s*', '', model_str, flags=re.IGNORECASE).strip()
        
        ver_m = re.search(r'Android\s+([\d.]+)', ua, re.IGNORECASE)
        android_ver = f"Android {ver_m.group(1)}" if ver_m else "Android"
        
        # In modern Chrome, model is often frozen as 'K'
        if model_str and model_str != 'K':
            phone_name = format_brand_model(model_str)
        else:
            phone_name = "Android Mobile (মডেল ডিটেক্ট হচ্ছে...)"
            
        return phone_name, "Android Phone", android_ver

    # Computers & Laptops
    if "windows" in ua_lower:
        win_ver = "Windows 11/10"
        if "windows nt 10.0" in ua_lower:
            win_ver = "Windows 11/10"
        elif "windows nt 6.3" in ua_lower:
            win_ver = "Windows 8.1"
        elif "windows nt 6.1" in ua_lower:
            win_ver = "Windows 7"
        return f"Desktop PC ({win_ver})", "Windows PC", win_ver

    if "macintosh" in ua_lower or "mac os" in ua_lower:
        return "Apple Mac / MacBook", "Mac Desktop/Laptop", "macOS"

    if "linux" in ua_lower:
        return "Linux Machine", "Linux PC", "Linux"
        
    return "Unknown Device", "Other", "Unknown"

def parse_browser(ua):
    if not ua:
        return "Unknown"
    ua_lower = ua.lower()
    if "edg/" in ua_lower or "edge/" in ua_lower:
        return "Microsoft Edge"
    elif "samsungbrowser" in ua_lower:
        return "Samsung Internet"
    elif "opr/" in ua_lower or "opera" in ua_lower:
        return "Opera"
    elif "chrome/" in ua_lower:
        return "Google Chrome"
    elif "firefox/" in ua_lower:
        return "Mozilla Firefox"
    elif "safari/" in ua_lower:
        return "Apple Safari"
    return "Web Browser"

def get_ip_geo(ip):
    # Local & Private IPs
    if not ip or ip in ('127.0.0.1', 'localhost', '::1') or ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.16.'):
        return "Bangladesh (Local)", "Dinajpur / Local", "Local Network", "Localhost / Wi-Fi"
    
    if ip in GEO_CACHE:
        return GEO_CACHE[ip]
    
    try:
        url = f"http://ip-api.com/json/{ip}?fields=country,regionName,city,isp,status"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('status') == 'success':
                country = data.get('country', 'Bangladesh')
                region = data.get('regionName', '')
                city = data.get('city', 'Unknown')
                isp = data.get('isp', 'Unknown ISP')
                
                isp_clean = isp
                isp_lower = isp.lower()
                if 'grameenphone' in isp_lower:
                    isp_clean = 'Grameenphone (4G/5G)'
                elif 'robi' in isp_lower:
                    isp_clean = 'Robi Axiata'
                elif 'banglalink' in isp_lower:
                    isp_clean = 'Banglalink'
                elif 'teletalk' in isp_lower:
                    isp_clean = 'Teletalk Bangladesh'
                    
                GEO_CACHE[ip] = (country, region, city, isp_clean)
                return country, region, city, isp_clean
    except Exception:
        pass
    
    GEO_CACHE[ip] = ("Online Visitor", "", "Unknown", "Public Network")
    return "Online Visitor", "", "Unknown", "Public Network"

def log_visitor_async(ip, path, method, phone_model, device, os_name, browser, ua, timestamp):
    try:
        country, region, city, isp = get_ip_geo(ip)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO visitors (ip, path, method, device, phone_model, os, browser, country, region, city, isp, user_agent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ip, path, method, device, phone_model, os_name, browser, country, region, city, isp, ua, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Tracker Log Error]: {e}")

def track_request(request):
    try:
        path = request.path
        # Ignore static assets, favicons, robots, telemetry
        if path.startswith('/static/') or path in ('/favicon.ico', '/robots.txt') or path.startswith('/api/admin/') or path == '/api/telemetry':
            return
        
        # Don't log the admin page visits itself
        if path in ('/admin-stats', '/visitors', '/admin'):
            return

        # Real Client IP from Proxies (Render / Cloudflare / Nginx)
        ip = (
            request.headers.get('CF-Connecting-IP') or
            (request.headers.get('X-Forwarded-For') or '').split(',')[0].strip() or
            request.remote_addr or
            'Unknown'
        )
        
        ua = request.headers.get('User-Agent', '')
        ch_model = request.headers.get('Sec-CH-UA-Model', '')
        
        phone_model, device, os_name = extract_phone_and_os(ua, ch_model)
        browser = parse_browser(ua)
        
        # Bangladesh Time (UTC+6)
        now_bd = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        timestamp = now_bd.strftime('%Y-%m-%d %I:%M:%S %p')
        method = request.method
        
        # Log asynchronously in background thread so user response is 0ms delay
        t = threading.Thread(
            target=log_visitor_async,
            args=(ip, path, method, phone_model, device, os_name, browser, ua, timestamp)
        )
        t.daemon = True
        t.start()
    except Exception as e:
        print(f"[Tracker Error]: {e}")

def update_telemetry_async(ip, data):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Find latest visitor matching IP or fallback to most recent row within last 60 seconds
        c.execute("SELECT id, ip, phone_model FROM visitors WHERE ip = ? ORDER BY id DESC LIMIT 1", (ip,))
        row = c.fetchone()
        if not row:
            c.execute("SELECT id, ip, phone_model FROM visitors ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            
        if not row:
            conn.close()
            return
        
        vid, curr_ip, curr_model = row
        updates = []
        params = []
        
        # 1. Real IP Replacement
        real_ip = data.get('real_ip')
        if real_ip and real_ip not in ('127.0.0.1', 'localhost', '::1', curr_ip):
            updates.append("ip = ?")
            params.append(real_ip)
            
        # 2. Location Info
        if data.get('city'):
            updates.append("city = ?")
            params.append(data['city'])
        if data.get('region'):
            updates.append("region = ?")
            params.append(data['region'])
        if data.get('country'):
            updates.append("country = ?")
            params.append(data['country'])
        if data.get('isp'):
            updates.append("isp = ?")
            params.append(data['isp'])
        if data.get('location_source'):
            updates.append("location_source = ?")
            params.append(data['location_source'])
            
        # 3. GPS Coordinates & Reverse Geocoding
        lat = data.get('lat')
        lon = data.get('lon')
        if lat is not None and lon is not None:
            updates.append("gps_lat = ?")
            params.append(float(lat))
            updates.append("gps_lon = ?")
            params.append(float(lon))
            if data.get('accuracy') is not None:
                updates.append("gps_accuracy = ?")
                params.append(float(data['accuracy']))
                
            # Perform reverse geocoding to find exact Place / Thana / Village
            place_name = reverse_geocode(lat, lon)
            if place_name:
                updates.append("exact_location = ?")
                params.append(place_name)
                
        # 4. Exact Phone Model
        exact_model = data.get('phone_model') or data.get('exact_model')
        if exact_model and str(exact_model).strip() and str(exact_model).strip() != 'K':
            formatted = format_brand_model(str(exact_model))
            updates.append("phone_model = ?")
            params.append(formatted)
            
        # 5. Hardware details
        if data.get('gpu'):
            updates.append("gpu = ?")
            params.append(str(data['gpu'])[:100])
        if data.get('screen'):
            updates.append("screen = ?")
            params.append(str(data['screen'])[:50])
        if data.get('ram'):
            updates.append("ram = ?")
            params.append(str(data['ram'])[:30])
            
        if updates:
            sql = f"UPDATE visitors SET {', '.join(updates)} WHERE id = ?"
            params.append(vid)
            c.execute(sql, params)
            conn.commit()
            
        conn.close()
    except Exception as e:
        print(f"[Telemetry Update Error]: {e}")

def update_telemetry(ip, data):
    t = threading.Thread(target=update_telemetry_async, args=(ip, data))
    t.daemon = True
    t.start()
    return True

def clear_all_logs():
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM visitors')
        c.execute('DELETE FROM sqlite_sequence WHERE name="visitors"')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Clear Logs Error]: {e}")
        return False

def get_stats(limit=150):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Total Visits
        c.execute('SELECT COUNT(*) FROM visitors')
        total_visits = c.fetchone()[0]
        
        # Unique IPs
        c.execute('SELECT COUNT(DISTINCT ip) FROM visitors')
        unique_visitors = c.fetchone()[0]
        
        # Today's Visits (BD date)
        now_bd = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        today_str = now_bd.strftime('%Y-%m-%d')
        c.execute("SELECT COUNT(*) FROM visitors WHERE timestamp LIKE ?", (f"{today_str}%",))
        today_visits = c.fetchone()[0]
        
        # Phone Models Breakdown
        c.execute('SELECT phone_model, COUNT(*) as count FROM visitors WHERE phone_model IS NOT NULL AND phone_model NOT LIKE "%মডেল ডিটেক্ট%" GROUP BY phone_model ORDER BY count DESC LIMIT 5')
        model_counts = [dict(row) for row in c.fetchall()]
        
        # Recent visitors list
        c.execute('''
            SELECT id, ip, path, method, device, phone_model, os, browser, country, region, city, exact_location, location_source, isp, 
                   gps_lat, gps_lon, gps_accuracy, gpu, screen, ram, timestamp 
            FROM visitors 
            ORDER BY id DESC 
            LIMIT ?
        ''', (limit,))
        recent_visitors = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "total_visits": total_visits,
            "unique_visitors": unique_visitors,
            "today_visits": today_visits,
            "model_counts": model_counts,
            "recent_visitors": recent_visitors,
            "server_time_bd": now_bd.strftime('%Y-%m-%d %I:%M:%S %p')
        }
    except Exception as e:
        return {"success": False, "error": str(e), "total_visits": 0, "unique_visitors": 0, "today_visits": 0, "recent_visitors": []}

init_db()
