# Vinyl Neo

A music discovery app built with Streamlit. Search for a song and it recommends similar tracks, or browse by genre, mood, or audio features. Recommendations come from the Spotify Web API when it's available. When it isn't, the app falls back to a content-based recommender: cosine similarity on audio features over a local 114k-track dataset.

**Live app:** [vinyl-neo.streamlit.app](https://vinyl-neo.streamlit.app/) (it runs on Streamlit Community Cloud, so if it's been idle, click "wake up" and give it about a minute)

<!-- Add a screenshot or GIF here: ![Vinyl Neo](assets/screenshot.png) -->

## What it does

| Page | What it does | Where the recommendations come from |
|---|---|---|
| **Search** | Type a song or artist. The top match is the seed, and recommendations are split into Side A (closest picks) and Side B (exploration). For local results, it shows a chart comparing the seed's audio features with each recommendation's. | Spotify first. Local cosine similarity if Spotify returns fewer than 5 tracks |
| **Discover** | Browse by genre, plus themed "crates" (Chill Lo-Fi, Late Night Jazz, …) | Spotify + local similarity |
| **Mood** | Mood-based picks with three modes: match my mood, shift brighter, lean into the feeling | Spotify + local dataset |
| **Playground** | Sliders for energy, valence, danceability, acousticness, and tempo | Spotify's tunable recommendations |
| **Playlists** | Liked songs, custom playlists, and a "remix" mode that chains a few tracks into a short side | Saved locally as JSON |

## How the local recommender works

1. Load `data/raw/spotify_tracks.csv` (about 114k tracks with Spotify audio features and genre labels).
2. Take six features: `danceability`, `energy`, `valence`, `acousticness`, `instrumentalness`, `speechiness`. Fill missing values with 0 and standardise each with `StandardScaler`.
3. Find the seed track by a case-insensitive match on track name, then on artist.
4. Rank every track by cosine similarity to the seed and return the top N, excluding the seed itself.

It's a straightforward content-based baseline. It knows nothing about users or listening history, only how a track sounds according to Spotify's audio features.

## Project structure

```
app.py                      home page and navigation
pages/                      search, discover, mood, playground, playlists, about
services/spotify_service.py Spotify Web API client (Client Credentials flow, token caching, timeouts)
utils/                      UI components, styling, JSON persistence for liked songs and playlists
config.py                   reads credentials from .env or Streamlit secrets; feature list and settings
data/raw/spotify_tracks.csv local track dataset
spotify_exploration.ipynb   data exploration
```

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

Then run:

```bash
streamlit run app.py
```

The app still works without Spotify credentials. Search falls back to the local dataset and the local recommender.

## Limitations

- **Spotify recommendations are unavailable, so the local model does the work.** In November 2024 Spotify restricted its Recommendations, Audio Features and 30-second preview endpoints for new Web API apps. On the live app, Spotify search still finds the seed track, but Spotify returns no recommendations, so every result comes from the local cosine-similarity recommender. Search, for example, shows 5 local picks instead of 20 from Spotify. The Mood and Playground pages also call Spotify's recommendations, so check how they behave without it.
- **No offline evaluation yet.** The recommendations haven't been measured against a held-out signal. So far they've only been judged by listening.
- **Name-based seed lookup.** The fallback finds the seed with a substring match on the track name, then the artist. A song that's missing from the local dataset, or spelled differently there, won't be found.
- **Brute-force similarity.** Each query compares against all 114k rows. That's fine at this size, but it wouldn't scale without an approximate nearest-neighbour index.
- **Local persistence only.** Liked songs and playlists live in a JSON file on the machine running the app.

## What I'd do next

- Evaluate the local recommender: treat same-genre or same-artist neighbours as a proxy for relevance, report precision@k against a random baseline and a genre-only baseline, and check how often the fallback can't find a seed.
- Add genre and tempo to the feature vector, and test whether that helps or just collapses recommendations into a single genre.
- Replace the brute-force search with an ANN index (FAISS or scikit-learn `NearestNeighbors`).
- Try audio or text embeddings (lyrics, tags) instead of six hand-picked features.
