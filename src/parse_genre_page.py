import re
from pathlib import Path

from bs4 import BeautifulSoup


def parse_artists(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for div in soup.find_all("div", id=re.compile(r"^item\d+$")):
        track = re.match(r'playx\("([A-Za-z0-9]+)"', div.get("onclick", ""))
        link = div.find("a", class_="navlink")
        artist = re.search(r"id=([A-Za-z0-9]+)", link["href"]) if link else None
        size = re.search(r"font-size:\s*(\d+)%", div.get("style", ""))
        name = next(div.stripped_strings, "")
        title = div.get("title", "")
        prefix = f"e.g. {name} "
        rows.append({
            "artist_id": artist.group(1) if artist else None,
            "name": name,
            "track_id": track.group(1) if track else None,
            "track_title": title[len(prefix):].strip('"') if title.startswith(prefix) else None,
            "size": int(size.group(1)) if size else None,
        })
    return rows


if __name__ == "__main__":
    rows = parse_artists(Path("data/shoegaze.html").read_text(encoding="utf-8"))
    print(len(rows), "artists")
    for r in rows[:3]:
        print(r)