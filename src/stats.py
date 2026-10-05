import sqlite3

from db import DB_PATH

con = sqlite3.connect(DB_PATH)

def one(sql: str):
    return con.execute(sql).fetchone()[0]


print("genres:", one("SELECT COUNT(*) FROM genres"))
print("pages fetched:", one("SELECT COUNT(*) FROM fetched"))
print("artists:", one("SELECT COUNT(*) FROM artists"))
print("genre-artist links:", one("SELECT COUNT(*) FROM genre_artists"))
print("genres with no artists:", one(
    "SELECT COUNT(*) FROM genres WHERE page NOT IN (SELECT page FROM genre_artists)"))
print("top artists by number of genres:")
for name, c in con.execute(
    "SELECT a.name, COUNT(*) c FROM genre_artists g JOIN artists a USING (artist_id) "
    "GROUP BY artist_id ORDER BY c DESC LIMIT 5"
):
    print("   ", name, c)