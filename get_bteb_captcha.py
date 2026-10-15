import requests
import base64

BASE = "http://result.bteb.gov.bd/api/public"
headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}

r = requests.get(f"{BASE}/captcha", headers=headers, timeout=5)
data = r.json()
print("Token:", data.get("token"))
print("Question:", data.get("question"))

img_data = data.get("image", "")
if img_data.startswith("data:image/png;base64,"):
    raw = base64.b64decode(img_data.split(",")[1])
    with open("bteb_captcha.png", "wb") as f:
        f.write(raw)
    print("Saved bteb_captcha.png, size:", len(raw))
