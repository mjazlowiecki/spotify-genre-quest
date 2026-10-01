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

1. **Collect** the genre list and the genre → artist mapping (Every Noise at Once snapshot).
2. **Select** artists with a greedy set-cover algorithm.
3. **Pick** one representative track per artist via the Spotify Web API.
4. **Order** tracks along a path through the genre map (nearest-neighbour heuristic).
5. **Build** the playlist and **track progress** from Spotify's extended streaming history.

## Status

Work in progress.

- [ ] Verify which Spotify API endpoints still work in Development Mode
- [ ] Genre and artist data collection
- [ ] Set-cover selection + coverage curve
- [ ] Track selection and ordering
- [ ] Playlist generation
- [ ] Progress tracker

## Limitations

- The genre list comes from a snapshot of Every Noise at Once (end of 2023); Spotify's
  taxonomy keeps changing, so coverage against today's genres is approximate.
- Spotify's Web API has become more restricted in recent years; parts of the pipeline
  may need to adapt.

## Disclaimer

This is an unofficial hobby project and is not affiliated with or endorsed by Spotify.
No Spotify data is redistributed in this repository.

## License

MIT, see [LICENSE](LICENSE). The license covers the code only.