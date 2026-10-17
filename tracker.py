import sqlite3
import os
import re
import datetime
import urllib.request
import json
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'visitors.db')
GEO_CACHE = {}

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
                os TEXT,
                browser TEXT,
                country TEXT,
                city TEXT,
                user_agent TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Tracker DB Init Error]: {e}")

def parse_user_agent(ua):
    if not ua:
        return "Unknown", "Unknown", "Unknown"
    
    ua_lower = ua.lower()
    
    # Check Bots first
    if any(b in ua_lower for b in ['bot', 'crawler', 'spider', 'curl', 'python', 'wget', 'slurp']):
        return "Bot / Crawler", "Automated Bot", "Bot"
    
    # OS & Device
    device = "Desktop"
    os_name = "Other"
    
    if "android" in ua_lower:
        device = "Android Phone"
        os_name = "Android"
    elif "iphone" in ua_lower:
        device = "iPhone"
        os_name = "iOS"
    elif "ipad" in ua_lower:
        device = "iPad"
        os_name = "iOS Tablet"
    elif "windows" in ua_lower:
        device = "Windows PC"
        os_name = "Windows"
    elif "macintosh" in ua_lower or "mac os" in ua_lower:
        device = "Mac Desktop/Laptop"
        os_name = "macOS"
    elif "linux" in ua_lower:
        device = "Linux Machine"
        os_name = "Linux"
        
    # Browser
    browser = "Unknown"
    if "edg/" in ua_lower or "edge/" in ua_lower:
        browser = "Microsoft Edge"
    elif "samsungbrowser" in ua_lower:
        browser = "Samsung Internet"
    elif "opr/" in ua_lower or "opera" in ua_lower:
        browser = "Opera"
    elif "chrome/" in ua_lower:
        browser = "Google Chrome"
    elif "firefox/" in ua_lower:
        browser = "Mozilla Firefox"
    elif "safari/" in ua_lower:
        browser = "Apple Safari"
        
    return device, os_name, browser

def get_ip_geo(ip):
    if not ip or ip in ('127.0.0.1', 'localhost', '::1') or ip.startswith('192.168.') or ip.startswith('10.'):
        return "Localhost / Local Network", "Local"
    
    if ip in GEO_CACHE:
        return GEO_CACHE[ip]
    
    try:
        url = f"http://ip-api.com/json/{ip}?fields=country,city,status"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.2) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown')
                city = data.get('city', 'Unknown')
                GEO_CACHE[ip] = (country, city)
                return country, city
    except Exception:
        pass
    
    GEO_CACHE[ip] = ("Online Visitor", "Unknown")
    return "Online Visitor", "Unknown"

def log_visitor_async(ip, path, method, device, os_name, browser, ua, timestamp):
    try:
        country, city = get_ip_geo(ip)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO visitors (ip, path, method, device, os, browser, country, city, user_agent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ip, path, method, device, os_name, browser, country, city, ua, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Tracker Log Error]: {e}")

def track_request(request):
    try:
        path = request.path
        # Ignore static assets, favicons, robots
        if path.startswith('/static/') or path in ('/favicon.ico', '/robots.txt') or path.startswith('/api/admin/'):
            return
        
        # Don't log the admin page visits itself to avoid noise
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
        device, os_name, browser = parse_user_agent(ua)
        
        # Bangladesh Time (UTC+6)
        now_bd = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        timestamp = now_bd.strftime('%Y-%m-%d %I:%M:%S %p')
        method = request.method
        
        # Log asynchronously in background thread so user response is instant (0ms delay)
        t = threading.Thread(
            target=log_visitor_async,
            args=(ip, path, method, device, os_name, browser, ua, timestamp)
        )
        t.daemon = True
        t.start()
    except Exception as e:
        print(f"[Tracker Error]: {e}")

def get_stats(limit=100):
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
        
        # Device Breakdown
        c.execute('SELECT device, COUNT(*) as count FROM visitors GROUP BY device ORDER BY count DESC LIMIT 5')
        device_counts = [dict(row) for row in c.fetchall()]
        
        # Recent visitors list
        c.execute('''
            SELECT id, ip, path, method, device, os, browser, country, city, timestamp 
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
            "device_counts": device_counts,
            "recent_visitors": recent_visitors,
            "server_time_bd": now_bd.strftime('%Y-%m-%d %I:%M:%S %p')
        }
    except Exception as e:
        return {"success": False, "error": str(e), "total_visits": 0, "unique_visitors": 0, "today_visits": 0, "recent_visitors": []}

init_db()
