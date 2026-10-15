import requests
import base64

BASE = "https://result.bteb.gov.bd"
r_cap = requests.get(f"{BASE}/api/public/captcha", headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
token = r_cap.json().get("token")
print("Raw token:", token)

# Decode token parts if separated by dot
for i, part in enumerate(token.split(".")):
    try:
        # pad base64
        padded = part + "=" * ((4 - len(part) % 4) % 4)
        decoded = base64.b64decode(padded)
        print(f"Part {i}: {decoded}")
    except Exception as e:
        print(f"Part {i}: (not b64: {part})")
