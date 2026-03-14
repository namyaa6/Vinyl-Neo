"""Feature playground: sliders to tune ML recommendation parameters. Local fallback always returns results."""
import streamlit as st
import pandas as pd

from utils.components import render_rec_card

st.set_page_config(layout="wide", page_title="Playground - Vinyl Neo")

@st.cache_data
def load_data():
    return pd.read_csv('data/raw/spotify_tracks.csv')

df = load_data()
feature_cols = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'speechiness']

if 'playground_recs' not in st.session_state:
    st.session_state.playground_recs = []
if 'playground_index' not in st.session_state:
    st.session_state.playground_index = 0
# Persist slider values so they survive rerun (e.g. when Spotify fails and we fall back to local)
if 'pg_energy' not in st.session_state:
    st.session_state.pg_energy = 0.5
if 'pg_valence' not in st.session_state:
    st.session_state.pg_valence = 0.5
if 'pg_danceability' not in st.session_state:
    st.session_state.pg_danceability = 0.5
if 'pg_acousticness' not in st.session_state:
    st.session_state.pg_acousticness = 0.3
if 'pg_min_tempo' not in st.session_state:
    st.session_state.pg_min_tempo = 80.0
if 'pg_max_tempo' not in st.session_state:
    st.session_state.pg_max_tempo = 160.0
if 'pg_genre' not in st.session_state:
    st.session_state.pg_genre = 'pop'
if 'liked_songs' not in st.session_state:
    st.session_state.liked_songs = []
if 'playlist_queue' not in st.session_state:
    st.session_state.playlist_queue = []

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .rec-card { background: #141010; padding: 40px; border-radius: 25px; text-align: center; border: 1px solid #2c1810; margin-top: 1rem; }
    .song-title { font-size: 1.8rem; font-weight: bold; margin-top: 16px; color: #f5e6d3; }
    .song-meta { color: #c4a574; font-size: 1rem; margin-top: 8px; }
    .stButton > button { background: #2c1810; color: #c4a574; border: 1px solid #4a3728; }
</style>
""", unsafe_allow_html=True)

if st.button('Back to menu', key='back_menu'):
    st.session_state.started = True
    st.switch_page("app.py")

st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">FEATURE PLAYGROUND</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Adjust audio features. See how recommendations change.</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    target_energy = st.slider('Target energy', 0.0, 1.0, st.session_state.pg_energy, 0.05, key='sl_energy')
    target_valence = st.slider('Target valence (mood)', 0.0, 1.0, st.session_state.pg_valence, 0.05, key='sl_valence')
    target_danceability = st.slider('Target danceability', 0.0, 1.0, st.session_state.pg_danceability, 0.05, key='sl_dance')
with col2:
    target_acousticness = st.slider('Target acousticness', 0.0, 1.0, st.session_state.pg_acousticness, 0.05, key='sl_acoustic')
    min_tempo = st.slider('Min tempo (BPM)', 60.0, 180.0, st.session_state.pg_min_tempo, 5.0, key='sl_min_tempo')
    max_tempo = st.slider('Max tempo (BPM)', 80.0, 200.0, st.session_state.pg_max_tempo, 5.0, key='sl_max_tempo')

seed_genre = st.selectbox(
    'Seed genre',
    ['pop', 'rock', 'electronic', 'jazz', 'acoustic', 'hip-hop', 'classical', 'indie'],
    index=['pop', 'rock', 'electronic', 'jazz', 'acoustic', 'hip-hop', 'classical', 'indie'].index(st.session_state.pg_genre),
    key='sl_genre',
)

if st.button('Get recommendations', use_container_width=True, key='playground_go'):
    # Persist slider values before any rerun
    st.session_state.pg_energy = target_energy
    st.session_state.pg_valence = target_valence
    st.session_state.pg_danceability = target_danceability
    st.session_state.pg_acousticness = target_acousticness
    st.session_state.pg_min_tempo = min_tempo
    st.session_state.pg_max_tempo = max_tempo
    st.session_state.pg_genre = seed_genre

    recs = []
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        if spotify._client_id:
            t_min, t_max = min_tempo, max_tempo
            if t_min > t_max:
                t_min, t_max = t_max, t_min
            tracks = spotify.get_recommendations_tunable(
                seed_genres=[seed_genre],
                limit=15,
                target_energy=target_energy,
                target_valence=target_valence,
                target_danceability=target_danceability,
                target_acousticness=target_acousticness,
                min_tempo=t_min,
                max_tempo=t_max,
            )
            for t in tracks:
                s = SpotifyService.simplify_track(t)
                recs.append({
                    'track_name': s.get('name'),
                    'artist': s.get('artist'),
                    'genre': seed_genre,
                    'preview_url': s.get('preview_url'),
                    'image_url': s.get('image_url'),
                    'external_url': s.get('external_url'),
                })
    except Exception as e:
        st.warning(f"Spotify unavailable. Using local dataset. ({e})")

    if not recs:
        # Local fallback: ensure we always get results
        subset = df.copy()
        subset['dist'] = (
            (subset['energy'].fillna(0) - target_energy) ** 2 +
            (subset['valence'].fillna(0) - target_valence) ** 2 +
            (subset['danceability'].fillna(0) - target_danceability) ** 2 +
            (subset['acousticness'].fillna(0) - target_acousticness) ** 2
        )
        t_lo, t_hi = min_tempo, max_tempo
        if t_lo > t_hi:
            t_lo, t_hi = t_hi, t_lo
        subset_tempo = subset[(subset['tempo'].fillna(120) >= t_lo) & (subset['tempo'].fillna(120) <= t_hi)]
        if len(subset_tempo) < 5:
            # Relax tempo filter so we have enough tracks
            subset_tempo = subset.nsmallest(20, 'dist')
        else:
            subset_tempo = subset_tempo.nsmallest(15, 'dist')
        for _, row in subset_tempo.iterrows():
            recs.append({
                'track_name': row['track_name'],
                'artist': row['artists'],
                'genre': row.get('track_genre', ''),
                'preview_url': None,
                'image_url': None,
                'external_url': None,
            })

    st.session_state.playground_recs = recs
    st.session_state.playground_index = 0
    st.success(f'Found {len(recs)} tracks')
    st.rerun()

if st.session_state.playground_recs:
    st.markdown('---')
    idx = min(st.session_state.playground_index, len(st.session_state.playground_recs) - 1)
    st.session_state.playground_index = idx
    rec = st.session_state.playground_recs[idx]

    def on_prev():
        if st.session_state.playground_index > 0:
            st.session_state.playground_index -= 1
            st.rerun()

    def on_next():
        if st.session_state.playground_index < len(st.session_state.playground_recs) - 1:
            st.session_state.playground_index += 1
            st.rerun()

    def on_like():
        song_data = {
            'name': rec.get('track_name', rec.get('name')),
            'artist': rec.get('artist', rec.get('artists', '')),
            'genre': rec.get('genre', ''),
            'preview_url': rec.get('preview_url'),
            'external_url': rec.get('external_url'),
        }
        if song_data not in st.session_state.liked_songs:
            st.session_state.liked_songs.append(song_data)
            st.success('Added to Liked Songs!')

    def on_add():
        st.session_state.playlist_queue.append(rec)
        st.info('Added to playlist queue')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_rec_card(rec, key_prefix='pg_rec', show_actions=True,
                        on_prev=on_prev, on_next=on_next, on_like=on_like, on_add_playlist=on_add)
    st.caption(f'{idx + 1} of {len(st.session_state.playground_recs)}')
