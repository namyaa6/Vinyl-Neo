"""Mood-based recommendations with contrast mode and shared rec card."""
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.components import render_rec_card, enrich_rec_with_spotify
from utils.user_data import ensure_user_session_loaded, save_user_data

st.set_page_config(layout="wide", page_title="Mood - Vinyl Neo")

MOOD_PROFILES = {
    'Chill': {'energy': 0.3, 'valence': 0.6, 'acousticness': 0.6, 'tempo': 90, 'spotify_genre': 'acoustic'},
    'Energetic': {'energy': 0.85, 'valence': 0.7, 'acousticness': 0.2, 'tempo': 130, 'spotify_genre': 'rock'},
    'Sad': {'energy': 0.3, 'valence': 0.2, 'acousticness': 0.5, 'tempo': 80, 'spotify_genre': 'acoustic'},
    'Happy': {'energy': 0.7, 'valence': 0.9, 'acousticness': 0.3, 'tempo': 120, 'spotify_genre': 'pop'},
    'Focus': {'energy': 0.4, 'valence': 0.5, 'acousticness': 0.4, 'instrumentalness': 0.3, 'tempo': 100, 'spotify_genre': 'classical'},
    'Party': {'energy': 0.9, 'valence': 0.8, 'danceability': 0.9, 'tempo': 125, 'spotify_genre': 'dance'},
}

# Internal keys -> display labels and captions
CONTRAST_OPTIONS = [
    ('neutral', 'Match my mood', ''),
    ('lift', 'Gradually shift to brighter', 'Adjusts valence and energy upward to gently improve your mood.'),
    ('deeper', 'Lean into the feeling', 'Lowers energy slightly for a more reflective, immersive experience.'),
]
CONTRAST_DELTAS = {
    'neutral': {'valence_delta': 0, 'energy_delta': 0},
    'lift': {'valence_delta': 0.3, 'energy_delta': 0.2},
    'deeper': {'valence_delta': -0.1, 'energy_delta': -0.2},
}

@st.cache_data
def load_data():
    return pd.read_csv('data/raw/spotify_tracks.csv')

df = load_data()

if 'mood_recs' not in st.session_state:
    st.session_state.mood_recs = []
if 'mood_index' not in st.session_state:
    st.session_state.mood_index = 0
if 'mood_history' not in st.session_state:
    st.session_state.mood_history = []
if 'mood_view' not in st.session_state:
    st.session_state.mood_view = 'moods'  # 'moods' | 'results'
if 'current_mood' not in st.session_state:
    st.session_state.current_mood = None
ensure_user_session_loaded(st.session_state)


def get_mood_recs(mood, contrast_key):
    """Spotify-first: genre-based recs from Spotify. Local CSV only as fallback."""
    base = MOOD_PROFILES.get(mood, MOOD_PROFILES['Chill']).copy()
    delta = CONTRAST_DELTAS.get(contrast_key, CONTRAST_DELTAS['neutral'])
    base['valence'] = min(1, max(0, base.get('valence', 0.5) + delta.get('valence_delta', 0)))
    base['energy'] = min(1, max(0, base.get('energy', 0.5) + delta.get('energy_delta', 0)))
    out = []
    # 1. Spotify first
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        genre = base.get('spotify_genre', 'pop')
        if spotify._client_id:
            tracks = spotify.get_recommendations_by_genres([genre], limit=15)
            for t in tracks:
                sim = SpotifyService.simplify_track(t)
                out.append({
                    'track_name': sim.get('name'),
                    'artist': sim.get('artist'),
                    'genre': genre,
                    'preview_url': sim.get('preview_url'),
                    'image_url': sim.get('image_url'),
                    'external_url': sim.get('external_url'),
                    'source': 'spotify',
                })
    except Exception:
        pass
    # 2. Local fallback if few Spotify recs
    if len(out) < 5:
        df_copy = df.copy()
        df_copy['score'] = 0.0
        for k, v in base.items():
            if k in df_copy.columns and k not in ('tempo', 'spotify_genre'):
                df_copy['score'] += -(df_copy[k].fillna(0) - v) ** 2
            elif k == 'tempo':
                df_copy['score'] += -((df_copy['tempo'].fillna(100) - v) / 100) ** 2
        for r in df_copy.nlargest(10, 'score').to_dict('records'):
            out.append({
                'track_name': r.get('track_name'),
                'artist': r.get('artists'),
                'genre': r.get('track_genre', ''),
                'track_id': r.get('track_id'),
            })
    return out


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

# Results view: replace mood selector with rec card + Back to moods
if st.session_state.mood_view == 'results' and st.session_state.mood_recs:
    if st.button('← Back to moods', key='back_moods'):
        st.session_state.mood_view = 'moods'
        st.session_state.mood_recs = []
        st.rerun()

    st.markdown(f'<h2 style="text-align: center; color: #c4a574;">{st.session_state.current_mood}</h2>', unsafe_allow_html=True)
    recs = st.session_state.mood_recs
    idx = min(st.session_state.mood_index, len(recs) - 1)
    st.session_state.mood_index = idx
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
        if st.session_state.mood_index > 0:
            st.session_state.mood_index -= 1
            st.rerun()

    def on_next():
        if st.session_state.mood_index < len(recs) - 1:
            st.session_state.mood_index += 1
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
        st.session_state.mood_history.append({
            'timestamp': datetime.now().isoformat(),
            'mood': st.session_state.current_mood,
            'tracks': [song_data],
        })

    def on_add():
        st.session_state.playlist_queue.append(rec_to_show)
        save_user_data(st.session_state.liked_songs, st.session_state.custom_playlists, st.session_state.playlist_queue)
        st.info('Added to playlist queue')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_rec_card(rec_to_show, key_prefix='mood_rec', show_actions=True,
                        on_prev=on_prev, on_next=on_next, on_like=on_like, on_add_playlist=on_add)
    st.caption(f'Track {idx + 1} of {len(recs)}')
    if st.session_state.mood_history:
        st.markdown('### Mood history')
        for entry in reversed(st.session_state.mood_history[-5:]):
            ts = entry['timestamp'][:19].replace('T', ' ')
            st.write(f"**{ts}** — {entry['mood']}")
    st.stop()

# Moods view
st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">MOOD</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Pick a mood and how you want to feel.</p>', unsafe_allow_html=True)

moods = list(MOOD_PROFILES.keys())
for row_start in range(0, len(moods), 3):
    cols = st.columns(3)
    for i, mood in enumerate(moods[row_start:row_start + 3]):
        with cols[i]:
            if st.button(mood, key=f'mood_{mood}', use_container_width=True):
                st.session_state.current_mood = mood

if st.session_state.current_mood:
    st.markdown('**Contrast**')
    contrast_choice = st.radio(
        'Contrast',
        options=[c[0] for c in CONTRAST_OPTIONS],
        format_func=lambda k: next(c[1] for c in CONTRAST_OPTIONS if c[0] == k),
        horizontal=True,
        key='contrast_radio',
    )
    cap = next((c[2] for c in CONTRAST_OPTIONS if c[0] == contrast_choice), '')
    if cap:
        st.caption(cap)
    if st.button('Get recommendations', key='mood_go'):
        recs = get_mood_recs(st.session_state.current_mood, contrast_choice)
        st.session_state.mood_recs = recs
        st.session_state.mood_index = 0
        st.session_state.mood_view = 'results'
        st.rerun()

if st.session_state.mood_history and st.session_state.mood_view == 'moods':
    st.markdown('### Mood history')
    for entry in reversed(st.session_state.mood_history[-10:]):
        ts = entry['timestamp'][:19].replace('T', ' ')
        st.write(f"**{ts}** — {entry['mood']}")
