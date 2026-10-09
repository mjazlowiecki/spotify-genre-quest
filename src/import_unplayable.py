import argparse
import re

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from build_playlist import api
from db import connect


def playlist_track_ids(auth, playlist_id):
    ids, offset, limit = [], 0, 50
    while True:
        try:
            page = api(auth, "GET", f"/playlists/{playlist_id}/items",
                       params={"limit": limit, "offset": offset})
        except RuntimeError as e:
            if limit > 10 and "-> 400" in str(e):
                limit = 10
                continue
            raise
        items = page.get("items", [])
        for entry in items:
            obj = entry.get("item") or entry.get("track") or {}
            if obj.get("id"):
                ids.append(obj["id"])
        offset += len(items)
        if not items or offset >= page.get("total", 0):
            return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("playlists", nargs="+", help="URLs or IDs of playlists with unavailable tracks")
    args = ap.parse_args()

    load_dotenv()
    auth = SpotifyOAuth(scope="playlist-read-private playlist-modify-private")
    con = connect()

    for source in args.playlists:
        m = re.search(r"playlist/([A-Za-z0-9]+)", source)
        playlist_id = m.group(1) if m else source
        ids = playlist_track_ids(auth, playlist_id)
        matched = unknown = 0
        for track_id in ids:
            rows = con.execute(
                "SELECT artist_id FROM artists WHERE track_id = ?", (track_id,)
            ).fetchall()
            if not rows:
                unknown += 1
                continue
            con.execute("INSERT OR REPLACE INTO availability VALUES (?, 0)", (track_id,))
            con.executemany("INSERT OR IGNORE INTO unplayable VALUES (?)", rows)
            matched += 1
        con.commit()
        print(f"{playlist_id}: {len(ids)} tracks read, {matched} marked unplayable, "
              f"{unknown} not found in the database")

    total = con.execute("SELECT COUNT(*) FROM unplayable").fetchone()[0]
    print("unplayable artists in total:", total)


if __name__ == "__main__":
    main()