import time
import urllib.request

URL = "https://bd-board-result-engine-1.onrender.com/api/health"

def main():
    print(f"[*] Render 24/7 Keep-Alive Daemon started for: {URL}", flush=True)
    while True:
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": "RenderKeepAlive/1.0"})
            with urllib.request.urlopen(req, timeout=30) as res:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping OK (HTTP {res.status})", flush=True)
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping Warning: {e}", flush=True)
        time.sleep(600)  # Ping every 10 minutes (600 seconds)

if __name__ == "__main__":
    main()
