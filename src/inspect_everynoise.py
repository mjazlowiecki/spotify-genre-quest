from pathlib import Path

import requests

Path("data").mkdir(exist_ok=True)
HEADERS = {"User-Agent": "genre-quest hobby project"}

PAGES = {
    "genre_map.html": "https://everynoise.com/engenremap.html",
    "shoegaze.html": "https://everynoise.com/engenremap-shoegaze.html",
}

for name, url in PAGES.items():
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.encoding = "utf-8"
    print(name, r.status_code, len(r.text))
    Path("data", name).write_text(r.text, encoding="utf-8")