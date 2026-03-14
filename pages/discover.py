"""Discover: browse by genre and themed crates. Clickable vinyls, shared rec card."""
import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

from utils.components import render_rec_card, enrich_rec_with_spotify
from utils.user_data import ensure_user_session_loaded, save_user_data

st.set_page_config(layout="wide", page_title="Discover - Vinyl Neo")

GENRE_TO_SPOTIFY = {
    'acoustic': 'acoustic', 'pop': 'pop', 'rock': 'rock', 'jazz': 'jazz',
    'hip-hop': 'hip-hop', 'electronic': 'electronic', 'classical': 'classical',
    'indie': 'indie', 'blues': 'blues', 'metal': 'metal', 'folk': 'folk',
    'dance': 'dance',
}

# Themed crates (merged from crates.py)
CRATES = [
    {"id": "chill", "name": "Chill Lo-Fi", "genre_contains": "acoustic", "max_energy": 0.5},
    {"id": "jazz", "name": "Late Night Jazz", "genre_contains": "jazz"},
    {"id": "electronic", "name": "Electronic Dreams", "genre_contains": "electronic"},
    {"id": "rock", "name": "90s Alt Rock", "genre_contains": "rock"},
    {"id": "indie", "name": "Indie Picks", "genre_contains": "indie"},
    {"id": "dance", "name": "Dance Floor", "genre_contains": "dance"},
]

@st.cache_data
def load_data():
    return pd.read_csv('data/raw/spotify_tracks.csv')

@st.cache_resource
def prepare_recommender(df):
    feature_cols = ['danceability', 'energy', 'valence', 'acousticness',
                    'instrumentalness', 'speechiness']
    feature_matrix = df[feature_cols].fillna(0)
    scaler = StandardScaler()
    return scaler.fit_transform(feature_matrix)

df = load_data()
feature_matrix = prepare_recommender(df)

if 'discover_view' not in st.session_state:
    st.session_state.discover_view = 'genres'  # 'genres' | 'results'
if 'discover_recs' not in st.session_state:
    st.session_state.discover_recs = []
if 'discover_rec_index' not in st.session_state:
    st.session_state.discover_rec_index = 0
if 'discover_selection_name' not in st.session_state:
    st.session_state.discover_selection_name = ''
ensure_user_session_loaded(st.session_state)


def get_genre_recommendations(genre_key):
    """Spotify-first: genre recs from Spotify (familiar tracks). Local CSV only as fallback."""
    recs = []
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        spotify_seed = GENRE_TO_SPOTIFY.get(genre_key, genre_key)
        if spotify._client_id:
            tracks = spotify.get_recommendations_by_genres([spotify_seed], limit=18)
            for t in tracks:
                sim = SpotifyService.simplify_track(t)
                recs.append({
                    'track_name': sim['name'],
                    'artist': sim['artist'],
                    'genre': genre_key,
                    'source': 'spotify',
                    'preview_url': sim.get('preview_url'),
                    'image_url': sim.get('image_url'),
                    'external_url': sim.get('external_url'),
                })
    except Exception:
        pass
    if len(recs) < 5:
        genre_songs = df[df['track_genre'].str.contains(genre_key, case=False, na=False)]
        if len(genre_songs) > 0:
            sample_idx = genre_songs.sample(1).index[0]
            song_features = feature_matrix[sample_idx].reshape(1, -1)
            similarities = cosine_similarity(song_features, feature_matrix)[0]
            for idx in similarities.argsort()[::-1]:
                row = df.iloc[idx]
                if genre_key.lower() in str(row['track_genre']).lower():
                    recs.append({
                        'track_name': row['track_name'],
                        'artist': row['artists'],
                        'genre': row['track_genre'],
                        'source': 'local_ml',
                        'track_id': row.get('track_id'),
                    })
                    if len(recs) >= 15:
                        break
    return recs


def load_crate(crate_def):
    """Themed crate: try Spotify genre first, fallback to local dataset."""
    genre = crate_def.get('genre_contains', '')
    recs = []
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        if spotify._client_id:
            tracks = spotify.get_recommendations_by_genres([genre], limit=15)
            for t in tracks:
                sim = SpotifyService.simplify_track(t)
                recs.append({
                    'track_name': sim['name'],
                    'artist': sim['artist'],
                    'genre': genre,
                    'source': 'spotify',
                    'preview_url': sim.get('preview_url'),
                    'image_url': sim.get('image_url'),
                    'external_url': sim.get('external_url'),
                })
    except Exception:
        pass
    if len(recs) < 5:
        subset = df[df['track_genre'].str.contains(genre, case=False, na=False)]
        if 'max_energy' in crate_def:
            subset = subset[subset['energy'] <= crate_def['max_energy']]
        if len(subset) > 0:
            sample = subset.sample(min(15, len(subset)))
            for _, row in sample.iterrows():
                recs.append({
                    'track_name': row['track_name'],
                    'artist': row['artists'],
                    'genre': row['track_genre'],
                    'source': 'local_ml',
                    'track_id': row.get('track_id'),
                })
    return recs


# Genre placeholder images (simple colored circles; can use Unsplash URLs later)
GENRE_COLORS = {
    'acoustic': '#8B7355', 'pop': '#E91E63', 'rock': '#9E9E9E', 'jazz': '#3F51B5',
    'hip-hop': '#FF9800', 'electronic': '#9C27B0', 'classical': '#795548',
    'indie': '#4CAF50', 'blues': '#2196F3', 'metal': '#424242', 'folk': '#8BC34A',
    'dance': '#00BCD4',
}

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .vinyl-btn { width: 140px; height: 140px; border-radius: 50% !important; font-weight: bold !important;
        text-transform: uppercase !important; margin: 0 auto 0.5rem !important; display: block !important;
        border: 4px solid #2c1810 !important; color: #f5e6d3 !important; }
    .genre-vinyl-grid .stButton > button { border-radius: 50% !important; width: 140px !important; height: 140px !important;
        margin: 0 auto !important; display: block !important; background: radial-gradient(circle, #2a2520 0%, #1a1510 100%) !important;
        border: 4px solid #2c1810 !important; color: #f5e6d3 !important; font-weight: bold !important; text-transform: uppercase !important; }
    .genre-vinyl-grid .stButton > button:hover { border-color: #c4a574 !important; transform: scale(1.05); }
    .rec-card { background: #141010; padding: 40px; border-radius: 25px; text-align: center; border: 1px solid #2c1810; margin-top: 1rem; }
    .song-title { font-size: 1.8rem; font-weight: bold; margin-top: 16px; color: #f5e6d3; }
    .song-meta { color: #c4a574; font-size: 1rem; margin-top: 8px; }
    .stButton > button { background-color: #2c1810; color: #c4a574; border: 1px solid #4a3728; }
    .stButton > button:hover { background-color: #4a3728; border-color: #c4a574; }
</style>
""", unsafe_allow_html=True)

if st.button('Back to menu', key='back_menu'):
    st.session_state.started = True
    st.switch_page("app.py")

if st.session_state.discover_view == 'results' and st.session_state.discover_recs:
    # Results view: replace grid with rec at top + Back to genres
    if st.button('← Back to genres', key='back_genres'):
        st.session_state.discover_view = 'genres'
        st.session_state.discover_recs = []
        st.rerun()

    st.markdown(f'<h2 style="text-align: center; color: #c4a574;">{st.session_state.discover_selection_name}</h2>', unsafe_allow_html=True)
    recs = st.session_state.discover_recs
    idx = min(st.session_state.discover_rec_index, len(recs) - 1)
    st.session_state.discover_rec_index = idx
    rec = recs[idx]

    # Enrich local recs with Spotify album art, preview, external_url
    rec_to_show = rec.copy()
    if not rec_to_show.get("preview_url") and not rec_to_show.get("image_url"):
        track_name = rec_to_show.get("track_name") or rec_to_show.get("name", "")
        artist = rec_to_show.get("artist") or rec_to_show.get("artists", "")
        en = enrich_rec_with_spotify(str(track_name), str(artist), rec_to_show.get("track_id"))
        if en:
            rec_to_show.update(en)

    def on_prev():
        if st.session_state.discover_rec_index > 0:
            st.session_state.discover_rec_index -= 1
            st.rerun()

    def on_next():
        if st.session_state.discover_rec_index < len(recs) - 1:
            st.session_state.discover_rec_index += 1
            st.rerun()

    def on_like():
        song_data = {
            'name': rec_to_show.get('track_name', rec_to_show.get('name')),
            'artist': rec_to_show.get('artist', rec_to_show.get('artists', '')),
            'genre': rec_to_show.get('genre', ''),
            'preview_url': rec_to_show.get('preview_url'),
            'external_url': rec_to_show.get('external_url'),
        }
        if song_data not in st.session_state.liked_songs:
            st.session_state.liked_songs.append(song_data)
            save_user_data(st.session_state.liked_songs, st.session_state.custom_playlists, st.session_state.playlist_queue)
            st.success('Added to Liked Songs!')

    def on_add():
        st.session_state.playlist_queue.append(rec_to_show)
        save_user_data(st.session_state.liked_songs, st.session_state.custom_playlists, st.session_state.playlist_queue)
        st.info('Added to playlist queue')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_rec_card(
            rec_to_show,
            key_prefix='discover_rec',
            show_actions=True,
            on_prev=on_prev,
            on_next=on_next,
            on_like=on_like,
            on_add_playlist=on_add,
        )
    st.caption(f'Track {idx + 1} of {len(recs)}')
    st.stop()

# Genres view
st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">DISCOVER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Click a genre or themed crate</p>', unsafe_allow_html=True)

# Genre vinyls: the button is the clickable vinyl (styled round)
st.markdown('<div class="genre-vinyl-grid">', unsafe_allow_html=True)
genres = ['acoustic', 'pop', 'rock', 'jazz', 'hip-hop', 'electronic',
          'classical', 'indie', 'blues', 'metal', 'folk', 'dance']

for row_start in range(0, len(genres), 4):
    cols = st.columns(4)
    for i, genre in enumerate(genres[row_start:row_start + 4]):
        with cols[i]:
            if st.button(genre.upper(), key=f'genre_{genre}', use_container_width=True):
                with st.spinner(f'Finding {genre} recommendations...'):
                    recs = get_genre_recommendations(genre)
                    st.session_state.discover_recs = recs
                    st.session_state.discover_rec_index = 0
                    st.session_state.discover_selection_name = f'{genre.upper()} — Recommendations'
                    st.session_state.discover_view = 'results'
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('---')
st.markdown('<h3 style="color: #c4a574;">Themed Crates</h3>', unsafe_allow_html=True)
crate_cols = st.columns(min(3, len(CRATES)))
for i, crate in enumerate(CRATES):
    with crate_cols[i % 3]:
        if st.button(crate['name'], key=f"crate_{crate['id']}", use_container_width=True):
            with st.spinner(f"Loading {crate['name']}..."):
                recs = load_crate(crate)
                st.session_state.discover_recs = recs
                st.session_state.discover_rec_index = 0
                st.session_state.discover_selection_name = crate['name']
                st.session_state.discover_view = 'results'
                st.rerun()
