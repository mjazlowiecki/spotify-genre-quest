import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("GENRE_QUEST_DB", ROOT / "data" / "genres.sqlite"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS genres (
    page TEXT PRIMARY KEY, name TEXT, x INTEGER, y INTEGER, size INTEGER,
    example_track_id TEXT, example TEXT
);
CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY, name TEXT, track_id TEXT, track_title TEXT
);
CREATE TABLE IF NOT EXISTS genre_artists (
    page TEXT, artist_id TEXT, size INTEGER, PRIMARY KEY (page, artist_id)
);
CREATE TABLE IF NOT EXISTS fetched (page TEXT PRIMARY KEY);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        con = sqlite3.connect(DB_PATH)
    except sqlite3.OperationalError as e:
        raise SystemExit(f"Cannot open database at {DB_PATH}: {e}")
    con.executescript(SCHEMA)
    return con