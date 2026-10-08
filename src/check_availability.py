import time
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

from db import connect

MARKET = "PL"
def main():
    load_dotenv()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(), retries=5)
    con = connect()
    rows = con.execute(
        "SELECT a.track_id FROM selection s JOIN artists a USING (artist_id) "
        "WHERE a.track_id NOT IN (SELECT track_id FROM availability)"
    ).fetchall()
    print(len(rows), "tracks to check")

    for i, (track_id,) in enumerate(rows, 1):
        try:
            track = sp.track(track_id, market=MARKET)
            playable = 1 if track.get("is_playable", False) else 0
        except spotipy.SpotifyException as e:
            if e.http_status != 404:
                print(f"{track_id}: HTTP {e.http_status}, will retry on next run")
                continue
            playable = 0
        con.execute("INSERT OR REPLACE INTO availability VALUES (?, ?)", (track_id, playable))
        if i % 100 == 0:
            con.commit()
            print(f"{i}/{len(rows)}")
        time.sleep(0.1)
    con.commit()

    con.execute(
        "INSERT OR IGNORE INTO unplayable "
        "SELECT a.artist_id FROM artists a JOIN availability v USING (track_id) WHERE v.playable = 0"
    )
    con.commit()
    bad = con.execute(
        "SELECT COUNT(*) FROM selection s JOIN artists a USING (artist_id) "
        "JOIN availability v USING (track_id) WHERE v.playable = 0"
    ).fetchone()[0]
    print(f"{bad} unplayable tracks in the current selection")


if __name__ == "__main__":
    main()