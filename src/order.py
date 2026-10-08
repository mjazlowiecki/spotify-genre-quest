from collections import defaultdict

import numpy as np

from db import connect

def artist_positions(con):
    genre_xy = {p: (x, y) for p, x, y in con.execute("SELECT page, x, y FROM genres")}
    acc = defaultdict(list)
    rows = con.execute(
        "SELECT s.artist_id, ga.page FROM selection s "
        "JOIN genre_artists ga ON ga.artist_id = s.artist_id"
    )
    for artist_id, page in rows:
        acc[artist_id].append(genre_xy[page])
    ids = list(acc)
    pts = np.array([np.mean(acc[a], axis=0) for a in ids], dtype=float)
    return ids, pts

def nearest_neighbour(pts, start):
    n = len(pts)
    visited = np.zeros(n, dtype=bool)
    order = [start]
    visited[start] = True
    for _ in range(n - 1):
        d = np.linalg.norm(pts - pts[order[-1]], axis=1)
        d[visited] = np.inf
        nxt = int(np.argmin(d))
        order.append(nxt)
        visited[nxt] = True
    return order


def path_length(pts, order):
    return float(np.linalg.norm(np.diff(pts[order], axis=0), axis=1).sum())


def main():
    con = connect()
    ids, pts = artist_positions(con)
    n = len(pts)

    order = nearest_neighbour(pts, start=int(np.argmin(pts[:, 1])))
    rng = np.random.default_rng(0)
    random_len = np.mean([path_length(pts, rng.permutation(n)) for _ in range(20)])
    ordered_len = path_length(pts, order)
    print(f"{n} artists")
    print(f"random order: {random_len:,.0f} px, nearest neighbour: {ordered_len:,.0f} px "
          f"({100 * ordered_len / random_len:.1f}% of random)")

    con.execute("DROP TABLE IF EXISTS playlist_order")
    con.execute("CREATE TABLE playlist_order (position INTEGER PRIMARY KEY, artist_id TEXT)")
    con.executemany(
        "INSERT INTO playlist_order VALUES (?, ?)",
        [(i, ids[j]) for i, j in enumerate(order, 1)],
    )
    con.commit()

    names = dict(con.execute("SELECT artist_id, name FROM artists"))
    for start in (1, 1000, 2000):
        print(f"positions {start}-{start + 5}:",
              ", ".join(names[ids[order[i - 1]]] for i in range(start, start + 6)))


if __name__ == "__main__":
    main()