import argparse
import time

import requests

from db import connect
from parse_genre_page import parse_artists

BASE = "https://everynoise.com/"
HEADERS = {"User-Agent": "genre-quest hobby project"}


def download(session: requests.Session, page: str, retries: int = 4) -> str | None:
    for attempt in range(retries):
        try:
            r = session.get(BASE + page, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                r.encoding = "utf-8"
                return r.text
            if r.status_code == 404:
                print(f"  {page}: 404, marking as done")
                return ""
            print(f"  {page}: HTTP {r.status_code}")
        except requests.RequestException as e:
            print(f"  {page}: {e!r}")
        time.sleep(5 * 2**attempt)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="process at most N pages")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    args = ap.parse_args()

    con = connect()
    pages = [p for (p,) in con.execute(
        "SELECT page FROM genres WHERE page NOT IN (SELECT page FROM fetched) ORDER BY page"
    )]
    if args.limit:
        pages = pages[: args.limit]
    print(len(pages), "pages to fetch")

    session = requests.Session()
    try:
        for i, page in enumerate(pages, 1):
            html = download(session, page)
            if html is None:
                print(f"  skipping {page} for now")
                continue
            rows = [r for r in parse_artists(html) if r["artist_id"]]
            con.executemany(
                "INSERT OR IGNORE INTO artists VALUES (?, ?, ?, ?)",
                [(r["artist_id"], r["name"], r["track_id"], r["track_title"]) for r in rows],
            )
            con.executemany(
                "INSERT OR IGNORE INTO genre_artists VALUES (?, ?, ?)",
                [(page, r["artist_id"], r["size"]) for r in rows],
            )
            con.execute("INSERT OR IGNORE INTO fetched VALUES (?)", (page,))
            if i % 25 == 0:
                con.commit()
                print(f"{i}/{len(pages)} done")
            time.sleep(args.delay)
    except KeyboardInterrupt:
        print("interrupted, progress saved")
    finally:
        con.commit()
        con.close()


if __name__ == "__main__":
    main()