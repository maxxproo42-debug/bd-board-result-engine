import requests
import base64
import ddddocr
from PIL import Image

ocr = ddddocr.DdddOcr(show_ad=False)
BASE = "https://result.bteb.gov.bd"

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://result.bteb.gov.bd",
    "Referer": "https://result.bteb.gov.bd/"
})

r_cap = s.get(f"{BASE}/api/public/captcha", timeout=5)
c_data = r_cap.json()
token = c_data.get("token")
img_b64 = c_data.get("image", "").split(",")[-1]
raw = base64.b64decode(img_b64)
with open("test_cap.png", "wb") as f:
    f.write(raw)

im = Image.open("test_cap.png")
w, h = im.size
pixels = im.convert("L").load()
for y in range(0, h, 2):
    line = "".join("#" if pixels[x, y] < 128 else " " for x in range(w))
    print(line)

cap_ans = ocr.classification(raw).strip()
print(f"Solved: {cap_ans}")
