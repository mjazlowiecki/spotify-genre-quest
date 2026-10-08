import argparse
import time

import requests
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from db import connect

API = "https://api.spotify.com/v1"


def api(auth, method, path, **kwargs):
    for _ in range(5):
        token = auth.get_access_token(as_dict=False)
        r = requests.request(
            method, API + path, headers={"Authorization": f"Bearer {token}"}, timeout=30, **kwargs
        )
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", "5"))
            if wait > 120:
                raise SystemExit(f"Rate limited, Retry-After {wait} s. Try again later.")
            time.sleep(wait + 1)
            continue
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:200]}")
        return r.json() if r.content else {}
    raise RuntimeError(f"{method} {path}: too many retries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only the first N tracks (for testing)")
    ap.add_argument("--name", default="Genre Quest")
    args = ap.parse_args()

    load_dotenv()
    auth = SpotifyOAuth(scope="playlist-modify-private")
    con = connect()

    rows = con.execute(
        "SELECT a.track_id, v.playable FROM playlist_order o "
        "JOIN artists a USING (artist_id) LEFT JOIN availability v USING (track_id) "
        "ORDER BY o.position"
    ).fetchall()
    known_bad = sum(1 for _, p in rows if p == 0)
    if known_bad:
        raise SystemExit(
            f"{known_bad} tracks are known to be unplayable: run set_cover.py and order.py first."
        )
    unverified = sum(1 for _, p in rows if p is None)
    print(f"{len(rows)} tracks, {unverified} not verified for availability")

    uris = list(dict.fromkeys(f"spotify:track:{t}" for t, _ in rows))
    if args.limit:
        uris = uris[: args.limit]
    print(len(uris), "tracks to add")

    playlist = api(auth, "POST", "/me/playlists", json={
        "name": args.name,
        "public": False,
        "description": "Every Noise genres, ordered along the genre map. Built with spotify-genre-quest.",
    })
    pid = playlist["id"]
    print("created:", playlist.get("external_urls", {}).get("spotify", pid))

    size, i = 100, 0
    while i < len(uris):
        try:
            api(auth, "POST", f"/playlists/{pid}/items", json={"uris": uris[i : i + size]})
        except RuntimeError as e:
            if size > 10 and "-> 400" in str(e):
                print("batch of 100 rejected, falling back to 10 per request")
                size = 10
                continue
            raise
        i += size
        time.sleep(0.2)
    print("done")


if __name__ == "__main__":
    main()