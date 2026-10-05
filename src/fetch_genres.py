import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from db import connect

BASE = "https://everynoise.com/"
HEADERS = {"User-Agent": "genre-quest hobby project"}
MAP_PATH = Path("data/genre_map.html")


def load_map_html() -> str:
    if MAP_PATH.exists():
        return MAP_PATH.read_text(encoding="utf-8")
    r = requests.get(BASE + "engenremap.html", headers=HEADERS, timeout=60)
    r.encoding = "utf-8"
    MAP_PATH.parent.mkdir(exist_ok=True)
    MAP_PATH.write_text(r.text, encoding="utf-8")
    return r.text


def parse_genres(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for div in soup.find_all("div", id=re.compile(r"^item\d+$")):
        link = div.find("a", class_="navlink")
        style = div.get("style", "")
        top = re.search(r"top:\s*(-?\d+)px", style)
        left = re.search(r"left:\s*(-?\d+)px", style)
        size = re.search(r"font-size:\s*(\d+)%", style)
        track = re.match(r'playx\("([A-Za-z0-9]+)"', div.get("onclick", ""))
        if not (link and top and left):
            continue
        rows.append({
            "page": link["href"],
            "name": next(div.stripped_strings, ""),
            "x": int(left.group(1)),
            "y": int(top.group(1)),
            "size": int(size.group(1)) if size else None,
            "example_track_id": track.group(1) if track else None,
            "example": div.get("title", "").removeprefix("e.g. "),
        })
    return rows


if __name__ == "__main__":
    rows = parse_genres(load_map_html())
    con = connect()
    con.executemany(
        "INSERT OR REPLACE INTO genres (page, name, x, y, size, example_track_id, example) "
        "VALUES (:page, :name, :x, :y, :size, :example_track_id, :example)",
        rows,
    )
    con.commit()
    print(len(rows), "genres saved")
    for r in rows[:3]:
        print(r)