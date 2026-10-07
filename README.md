# Spotify Genre Quest

> One playlist. As many Spotify genres as possible.

## Why

Spotify Wrapped tells you how many genres you listened to, but not how those genres
are defined, and not how many exist. This project started as a half-joke challenge
("listen to every genre Spotify knows") and turned into an exercise in data collection,
combinatorial optimization and playlist design.

Spotify tags *artists*, not tracks, with thousands of fine-grained micro-genres
(shoegaze, nu metal, escape room, ...). Instead of picking one track per genre, this
project treats the problem as **set cover**: find a small set of artists whose genres
together cover as much of the genre list as possible, then order the tracks so the
playlist flows logically through genre space.

## Approach

1. **Collect** the genre map (names, positions, example tracks) from an Every Noise at Once snapshot.
2. **Baseline:** one example track per genre, ordered along a path through the genre map (nearest-neighbour heuristic).
3. **Optimization (planned):** greedy set cover over per-genre artist lists, covering the same genres with fewer tracks.
4. **Verify** track availability via the Spotify Web API and **build** the playlist.
5. **Track progress** from Spotify's extended streaming history.

## Status

- [x] Verify which Spotify API endpoints still work in Development Mode
- [x] Genre map collection (6,291 genres)
- [ ] Baseline playlist: one track per genre, ordered along the genre map
- [x] Set-cover optimization + coverage curve
- [ ] Playlist generation
- [ ] Progress tracker

## Findings

- In Development Mode the artist object no longer includes `genres`, so genres cannot be read from the Spotify API.
- `recommendations/available-genre-seeds` and artist top tracks are unavailable.
- Every Noise at Once (snapshot through 2023-11-19, 6,291 genres) exposes Spotify artist and example-track IDs for each genre. These IDs were verified against the Spotify API: artist and track lookups work and tracks are playable.

## Limitations

- The genre list comes from a snapshot of Every Noise at Once (end of 2023); Spotify's
  taxonomy keeps changing, so coverage against today's genres is approximate.
- Spotify's Web API has become more restricted in recent years; parts of the pipeline
  may need to adapt.

## Results

| | Tracks | Listening time* |
|---|---|---|
| One track per genre (baseline) | 6,291 | ~367 h |
| Greedy set cover | 2,697 | ~157 h |

\*Assuming 3.5 minutes per track (the data has no track durations).

All 6,291 genres of the snapshot are covered by 2,697 artists (43% of the baseline).
About a third of the picks (925) each add only a single new genre: the long tail.
Artists without an example track in the snapshot (~24k of ~481k) were excluded.

![Coverage curve](docs/coverage.png)

## Disclaimer

This is an unofficial hobby project and is not affiliated with or endorsed by Spotify.
No Spotify or Every Noise data is redistributed in this repository.

## Acknowledgements

Genre data comes from [Every Noise at Once](https://everynoise.com/) by Glenn McDonald:
a snapshot of Spotify's genre taxonomy through 2023-11-19. This project is not affiliated
with him or with Spotify.

## License

MIT, see [LICENSE](LICENSE). The license covers the code only.
