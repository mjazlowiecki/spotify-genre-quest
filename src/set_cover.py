import csv
import heapq
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from db import ROOT, connect

AVG_TRACK_MINUTES = 3.5     #assumed, as the data has no track durations

def load(con):
        all_genres = {p for (p,) in con.execute("SELECT page FROM genres")}
        artist_genres = defaultdict(dict) #artist_id -> {genre page: prominence}
        rows = con.execute(
            "SELECT ga.artist_id, ga.page, COALESCE(ga.size, 100) "
            "FROM genre_artists ga JOIN artists a ON a.artist_id = ga.artist_id "
            "WHERE a.track_id IS NOT NULL "
            "AND ga.artist_id NOT IN (SELECT artist_id FROM unplayable)"
        )
        for artist_id, page, size in rows:
            artist_genres[artist_id][page] = size
        return all_genres, artist_genres

def gain_and_prominence(genres, covered):
    gain = prom = 0
    for page,size in genres.items():
        if page not in covered:
            gain += 1
            prom += size
    return gain, prom

def greedy(all_genres, artist_genres):
    covered = set()
    heap = [(-len(gs), -sum(gs.values()), a) for a, gs in artist_genres.items()]
    heapq.heapify(heap)
    picks = [] # (artist_id, gain, covered_after)
    while heap and len(covered) < len (all_genres):
        _, _, artist_id = heapq.heappop(heap)
        gain, prom = gain_and_prominence(artist_genres[artist_id], covered)
        if gain == 0:
            continue
        entry = (-gain, -prom, artist_id)
        if heap and entry > heap[0]: # stale score -> re-queue and try the next one?
            heapq.heappush(heap, entry)
            continue
        covered.update(artist_genres[artist_id])
        picks.append((artist_id, gain, len(covered)))
    return picks, covered

def main():
    con = connect()
    all_genres, artist_genres = load(con)
    total = len(all_genres)
    print(f"{len(artist_genres)} candidate artists, {total} genres")

    picks, covered = greedy(all_genres, artist_genres)
    n = len(picks)
    print(f"covered {len(covered)}/{total} genres with {n} artists")
    if len(covered) < total:
        print(f"WARNING: {total - len(covered)} genres could not be covered")
    hours = lambda tracks: tracks * AVG_TRACK_MINUTES / 60
    print(f"baseline (1 track per genre): {total} tracks, ~{hours(total):.0f} h")
    print(f"greedy set cover: {n} tracks, ~{hours(n):.0f} h "
          f"({100 * n / total:.0f}% of baseline; assuming {AVG_TRACK_MINUTES} min/track)")
    print("picks that add exactly 1 genre:", sum(1 for _, g, _ in picks if g == 1))
    print("top picks:")
    for rank, (artist_id, gain, _) in enumerate(picks[:10], 1):
        name = con.execute("SELECT name FROM artists WHERE artist_id = ?", (artist_id,)).fetchone()[0]
        print(f"  {rank:>2}. {name} (+{gain})")

    con.execute("DROP TABLE IF EXISTS selection")
    con.execute(
        "CREATE TABLE selection (rank INTEGER PRIMARY KEY, artist_id TEXT, gain INTEGER, covered INTEGER)"
    )
    con.executemany(
        "INSERT INTO selection VALUES (?, ?, ?, ?)",
        [(i, a, g, c) for i, (a, g, c) in enumerate(picks, 1)],
    )
    con.commit()

    with open(ROOT / "data" / "coverage_curve.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tracks", "genres_covered"])
        for i, (_, _, c) in enumerate(picks, 1):
            w.writerow([i, c])

    (ROOT / "docs").mkdir(exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, n + 1), [c for _, _, c in picks], label="greedy set cover")
    plt.plot([0, total], [0, total], "--", label="one track per genre (baseline)")
    plt.xlabel("tracks in playlist")
    plt.ylabel("genres covered")
    plt.title("Coverage of Every Noise genres (snapshot through 2023-11-19)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ROOT / "docs" / "coverage.png", dpi=150)
    print("saved docs/coverage.png")

if __name__ == "__main__":
    main()



