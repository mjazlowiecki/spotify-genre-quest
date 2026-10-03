import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())


def attempt(label, fn):
    try:
        result = fn()
        print(f"[OK]   {label}")
        return result
    except spotipy.SpotifyException as e:
        print(f"[FAIL] {label} -> HTTP {e.http_status}: {str(e.msg)[:120]}")
    except Exception as e:
        print(f"[FAIL] {label} -> {e!r}")
    return None


res = attempt(
    'search artist genre:"shoegaze"',
    lambda: sp.search(q='genre:"shoegaze"', type="artist", limit=10),
)
artist_ids = []
if res:
    for a in res["artists"]["items"]:
        artist_ids.append(a["id"])
        print("    ", a["name"], "| genres:", a.get("genres", "<no genres field>"))

if artist_ids:
    a = attempt("artist (single)", lambda: sp.artist(artist_ids[0]))
    if a:
        print("     genres field present:", "genres" in a, "->", a.get("genres"))

if len(artist_ids) >= 2:
    attempt("artists (batch)", lambda: sp.artists(artist_ids[:2]))

tr = attempt(
    'search track artist:"Slowdive"',
    lambda: sp.search(q='artist:"Slowdive"', type="track", limit=5, market="PL"),
)
if tr:
    for t in tr["tracks"]["items"]:
        print("    ", t["name"], "-", t["artists"][0]["name"])


attempt("recommendation genre seeds", lambda: sp.recommendation_genre_seeds())
if artist_ids:
    attempt("artist top tracks", lambda: sp.artist_top_tracks(artist_ids[0], country="PL"))

    a = attempt("artist by Every Noise id", lambda: sp.artist("72X6FHxaShda0XeQw3vbeF"))
    if a:
        print("    ", a["name"])  # oczekiwane: Slowdive

    t = attempt("track by Every Noise id", lambda: sp.track("0oxYB9GoOIDrdzniNdKC44", market="PL"))
    if t:
        print("    ", t["name"], "| playable:", t.get("is_playable"))