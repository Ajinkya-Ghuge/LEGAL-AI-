import urllib.request
import os

os.makedirs("backend/static/css", exist_ok=True)
url = "https://cdn.tailwindcss.com/3.4.1/tailwind.min.css"
out = "backend/static/css/tailwind.min.css"
print("Downloading Tailwind CSS...")
urllib.request.urlretrieve(url, out)
size = os.path.getsize(out)
print(f"Done! Saved to {out} ({size//1024}KB)")
