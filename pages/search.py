import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

from utils.components import render_rec_card

st.set_page_config(layout="wide", page_title="Search - Vinyl Neo")

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
feature_cols = ['danceability', 'energy', 'valence', 'acousticness',
                'instrumentalness', 'speechiness']

# Session state
if 'current_rec_index' not in st.session_state:
    st.session_state.current_rec_index = 0
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'liked_songs' not in st.session_state:
    st.session_state.liked_songs = []
if 'custom_playlists' not in st.session_state:
    st.session_state.custom_playlists = {}
if 'playlist_queue' not in st.session_state:
    st.session_state.playlist_queue = []
if 'current_side' not in st.session_state:
    st.session_state.current_side = 'A'
if 'side_a' not in st.session_state:
    st.session_state.side_a = []
if 'side_b' not in st.session_state:
    st.session_state.side_b = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
if 'seed_track' not in st.session_state:
    st.session_state.seed_track = None  # { name, artist, genre, image_url, preview_url, ... }
if 'search_box' not in st.session_state:
    st.session_state.search_box = ''

# Clear rec state when search box is empty (fresh load or user cleared)
if st.session_state.get('search_box', '') == '':
    if st.session_state.get('recommendations') or st.session_state.get('side_a'):
        st.session_state.recommendations = []
        st.session_state.side_a = []
        st.session_state.side_b = []
        st.session_state.current_rec_index = 0
        st.session_state.seed_features = None
        st.session_state.liner_notes = None
        st.session_state.seed_track = None
        st.session_state.search_query = None


def get_hybrid_recommendations(track_name, artist_name, track_id, df, feature_matrix, n_local=10, n_spotify=10):
    """Combine local ML recommendations with Spotify similar tracks."""
    recommendations = []

    # 1. Local content-based
    matches = df[df['track_name'].str.contains(track_name, case=False, na=False)]
    if len(matches) == 0:
        matches = df[df['artists'].str.contains(artist_name, case=False, na=False)]
    if len(matches) > 0:
        song_idx = matches.index[0]
        song_features = feature_matrix[song_idx].reshape(1, -1)
        similarities = cosine_similarity(song_features, feature_matrix)[0]
        similar_indices = similarities.argsort()[::-1][1:n_local + 1]
        for idx in similar_indices:
            row = df.iloc[idx]
            recommendations.append({
                'track_name': row['track_name'],
                'artist': row['artists'],
                'genre': row['track_genre'],
                'source': 'local_ml',
                'score': float(similarities[idx]),
                'track_id': row.get('track_id'),
                'features': {c: row.get(c, 0) for c in feature_cols if c in row},
            })

    # 2. Spotify
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        if track_id and spotify._client_id:
            spotify_tracks = spotify.get_recommendations_by_tracks([str(track_id)], limit=n_spotify)
            for track in spotify_tracks:
                sim = SpotifyService.simplify_track(track)
                recommendations.append({
                    'track_name': sim['name'],
                    'artist': sim['artist'],
                    'genre': '',
                    'source': 'spotify',
                    'score': 0.8,
                    'track_id': sim.get('spotify_id'),
                    'preview_url': sim.get('preview_url'),
                    'image_url': sim.get('image_url'),
                    'external_url': sim.get('external_url'),
                })
    except Exception:
        pass

    return recommendations


def split_sides(recs, n_per_side=6):
    side_a = recs[:n_per_side]
    side_b = recs[n_per_side:n_per_side * 2] if len(recs) > n_per_side else []
    return side_a, side_b


def generate_liner_notes(recs, mood=None):
    if not recs:
        return "No tracks yet."
    sources = [r.get('source', '') for r in recs]
    local = sum(1 for s in sources if s == 'local_ml')
    spotify = sum(1 for s in sources if s == 'spotify')
    parts = []
    if local:
        parts.append(f"{local} from our ML similarity engine")
    if spotify:
        parts.append(f"{spotify} from Spotify")
    blend = " and ".join(parts)
    import random
    labels = ["Late-night lo-fi walk", "Bright morning spins", "Deep dive session", "Curated discovery"]
    label = random.choice(labels) if not mood else f"{mood} session"
    return f"{label}. Blending {blend}."


@st.cache_data(ttl=3600)
def enrich_local_rec_with_spotify(track_name, artist_name, track_id):
    """Fetch album art and preview for a local track via Spotify search."""
    if not track_id:
        return None
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        q = f"{track_name} {artist_name}"
        items = spotify.search_track(q, limit=3)
        for track in items:
            sim = SpotifyService.simplify_track(track)
            if sim.get('preview_url') or sim.get('image_url'):
                return {'image_url': sim.get('image_url'), 'preview_url': sim.get('preview_url'), 'external_url': sim.get('external_url')}
    except Exception:
        pass
    return None


def search_spotify_track(query):
    """Search Spotify by query. Returns (track_name, artist, track_id, ...) or None. Raises on error for surfacing."""
    from services.spotify_service import SpotifyService
    spotify = SpotifyService()
    if not spotify._client_id or not spotify._client_secret:
        raise ValueError(
            "Spotify credentials not found. "
            "Locally: add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to .env. "
            "On Streamlit Cloud: add them in Settings → Secrets (top-level keys, no spaces in values)."
        )
    items = spotify.search_track(query, limit=5)
    if not items:
        return None
    sim = SpotifyService.simplify_track(items[0])
    return {
        'track_name': sim.get('name'),
        'artist': sim.get('artist'),
        'track_id': sim.get('spotify_id'),
        'image_url': sim.get('image_url'),
        'preview_url': sim.get('preview_url'),
        'external_url': sim.get('external_url'),
    }


# Inject rec-card styles (shared with assets/style.css)
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .rec-card { background: #141010; padding: 40px; border-radius: 25px; text-align: center; border: 1px solid #2c1810; margin-top: 1rem; }
    .song-title { font-size: 1.8rem; font-weight: bold; margin-top: 16px; color: #f5e6d3; }
    .song-meta { color: #c4a574; font-size: 1rem; margin-top: 8px; }
    .stButton > button { background-color: #2c1810; color: #c4a574; border: 1px solid #4a3728; }
    .stButton > button:hover { background-color: #4a3728; border-color: #c4a574; }
</style>
""", unsafe_allow_html=True)

# Back to menu
if st.button('Back to menu', key='back_menu'):
    st.session_state.started = True
    st.switch_page("app.py")

st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">SEARCH</h1>', unsafe_allow_html=True)

# Single search bar (search both track_name and artists automatically)
search_query = st.text_input(
    '',
    placeholder='Search by song name or artist...',
    label_visibility='collapsed',
    key='search_box',
)
# Keep "last search that produced results" in session for state clearing
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
# When user submits search we set search_query to the box value below

if st.button('SEARCH', use_container_width=True, key='search_btn'):
    if search_query:
        with st.spinner('Finding recommendations...'):
            track_name = None
            artist_name = None
            track_id = None
            row = None

            # 1. Try local CSV first
            matches = df[df['track_name'].str.contains(search_query, case=False, na=False)]
            if len(matches) == 0:
                matches = df[df['artists'].str.contains(search_query, case=False, na=False)]
            if len(matches) > 0:
                row = matches.iloc[0]
                track_name = row['track_name']
                artist_name = row['artists']
                track_id = str(row.get('track_id', '')) if pd.notna(row.get('track_id')) else None

            # 2. If not in CSV, try Spotify search (e.g. "Ordinary by Alex Warren")
            spotify_result = None
            spotify_error = None
            if track_name is None:
                try:
                    spotify_result = search_spotify_track(search_query)
                except Exception as e:
                    spotify_error = str(e)
                if spotify_result:
                    track_name = spotify_result['track_name']
                    artist_name = spotify_result['artist']
                    track_id = spotify_result.get('track_id')
                    row = None  # No CSV row for features

            if track_name is not None and artist_name is not None:
                st.session_state.search_query = search_query
                hybrid_recs = get_hybrid_recommendations(
                    track_name, artist_name, track_id, df, feature_matrix
                )
                side_a, side_b = split_sides(hybrid_recs)
                st.session_state.side_a = side_a
                st.session_state.side_b = side_b
                st.session_state.recommendations = side_a
                st.session_state.current_side = 'A'
                st.session_state.current_rec_index = 0
                st.session_state.liner_notes = generate_liner_notes(hybrid_recs)

                if row is not None:
                    st.session_state.seed_features = {c: float(row.get(c, 0)) for c in feature_cols if c in row}
                else:
                    st.session_state.seed_features = None

                # Seed track: from Spotify search or enriched from local CSV
                seed_image = None
                seed_preview = None
                seed_external = None
                seed_genre = row.get('track_genre', '') if row is not None else ''
                if spotify_result:
                    seed_image = spotify_result.get('image_url')
                    seed_preview = spotify_result.get('preview_url')
                    seed_external = spotify_result.get('external_url')
                elif row is not None and track_id:
                    enriched = enrich_local_rec_with_spotify(track_name, artist_name, track_id)
                    if enriched:
                        seed_image = enriched.get('image_url')
                        seed_preview = enriched.get('preview_url')
                        seed_external = enriched.get('external_url')

                st.session_state.seed_track = {
                    'name': track_name,
                    'artist': artist_name,
                    'genre': seed_genre,
                    'image_url': seed_image,
                    'preview_url': seed_preview,
                    'external_url': seed_external,
                }
                st.rerun()
            else:
                if spotify_error:
                    st.error(spotify_error)
                else:
                    st.error('No results found. Try a different search.')

# Results: left 40% = searched track, right 60% = current rec + actions + feature comparison
all_recs = st.session_state.side_a if st.session_state.current_side == 'A' else st.session_state.side_b
if not all_recs:
    all_recs = st.session_state.recommendations

if all_recs and st.session_state.seed_track:
    idx = min(st.session_state.current_rec_index, len(all_recs) - 1)
    st.session_state.current_rec_index = idx
    rec = all_recs[idx]
    seed = st.session_state.seed_track

    st.markdown('---')
    st.markdown(
        f'<p style="text-align: center; color: #888;">'
        f'Side {st.session_state.current_side}: Similar · Track {idx + 1} of {len(all_recs)}'
        f'</p>',
        unsafe_allow_html=True,
    )

    # Enrich local recs with Spotify preview/art when possible
    rec_to_show = rec.copy()
    if not rec_to_show.get('preview_url') and not rec_to_show.get('image_url') and rec_to_show.get('track_id'):
        en = enrich_local_rec_with_spotify(
            rec_to_show.get('track_name', rec_to_show.get('name', '')),
            rec_to_show.get('artist', rec_to_show.get('artists', '')),
            rec_to_show['track_id'],
        )
        if en:
            rec_to_show.update(en)

    col_left, col_right = st.columns([2, 3])  # 40% / 60%
    with col_left:
        st.markdown('**Your pick**')
        if seed.get('image_url'):
            st.image(seed['image_url'], width=200)
        else:
            st.markdown('<div style="width:200px;height:200px;border-radius:50%;background:#1a1a1a;border:6px solid #2c1810;"></div>', unsafe_allow_html=True)
        st.markdown(f"**{seed['name']}**  \n{seed['artist']}  \n{seed.get('genre', '')}")
        if seed.get('preview_url'):
            st.audio(seed['preview_url'])
        if seed.get('external_url'):
            st.link_button('Open in Spotify', url=seed['external_url'], type='secondary')

    with col_right:
        def on_prev():
            if st.session_state.current_rec_index > 0:
                st.session_state.current_rec_index -= 1
                st.rerun()

        def on_next():
            if st.session_state.current_rec_index < len(all_recs) - 1:
                st.session_state.current_rec_index += 1
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
                st.success('Added to Liked Songs!')

        def on_add():
            st.session_state.playlist_queue.append(rec_to_show)
            st.info('Added to playlist queue')

        render_rec_card(
            rec_to_show,
            key_prefix='search_rec',
            show_actions=True,
            on_prev=on_prev,
            on_next=on_next,
            on_like=on_like,
            on_add_playlist=on_add,
        )

        # Side A / Side B toggle and caption
        st.caption('Side A = tracks closest to your search. Side B = tracks that push boundaries.')
        side_label = 'Side A: Similar' if st.session_state.current_side == 'A' else 'Side B: Explore'
        if st.button(side_label, key='side_toggle'):
            st.session_state.current_side = 'B' if st.session_state.current_side == 'A' else 'A'
            st.session_state.recommendations = st.session_state.side_b if st.session_state.current_side == 'B' else st.session_state.side_a
            st.session_state.current_rec_index = 0
            st.rerun()

        # Feature comparison (one-line interpretation + chart)
        if rec_to_show.get('features') and st.session_state.get('seed_features'):
            seed_f = st.session_state.seed_features
            rec_f = rec_to_show['features']
            f_names = [c for c in feature_cols if c in seed_f and c in rec_f]
            if f_names:
                diffs = [(c, rec_f.get(c, 0) - seed_f.get(c, 0)) for c in f_names]
                higher = [c for c, d in diffs if d > 0.1]
                lower = [c for c, d in diffs if d < -0.1]
                if higher or lower:
                    line = "This track has "
                    if higher:
                        line += "higher " + ", ".join(higher)
                    if lower:
                        if higher:
                            line += " but "
                        line += "lower " + ", ".join(lower)
                    line += " compared to your pick."
                else:
                    line = "This track has similar audio features to your pick."
                st.caption(line)
                chart_data = pd.DataFrame({
                    'Your pick': [seed_f.get(c, 0) for c in f_names],
                    'This track': [rec_f.get(c, 0) for c in f_names],
                }, index=f_names)
                st.bar_chart(chart_data)

    if st.session_state.get('liner_notes'):
        with st.expander('Liner notes'):
            st.write(st.session_state.liner_notes)

elif all_recs:
    # No seed_track stored (legacy or first run) – still show recs
    idx = min(st.session_state.current_rec_index, len(all_recs) - 1)
    st.session_state.current_rec_index = idx
    rec = all_recs[idx]
    rec_to_show = rec.copy()
    if not rec_to_show.get('preview_url') and not rec_to_show.get('image_url') and rec_to_show.get('track_id'):
        en = enrich_local_rec_with_spotify(
            rec_to_show.get('track_name', rec_to_show.get('name', '')),
            rec_to_show.get('artist', rec_to_show.get('artists', '')),
            rec_to_show['track_id'],
        )
        if en:
            rec_to_show.update(en)
    st.markdown('---')
    col_left, col_right = st.columns([2, 3])
    with col_right:
        def on_prev():
            if st.session_state.current_rec_index > 0:
                st.session_state.current_rec_index -= 1
                st.rerun()
        def on_next():
            if st.session_state.current_rec_index < len(all_recs) - 1:
                st.session_state.current_rec_index += 1
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
                st.success('Added to Liked Songs!')
        def on_add():
            st.session_state.playlist_queue.append(rec_to_show)
            st.info('Added to playlist queue')
        render_rec_card(rec_to_show, key_prefix='search_rec', show_actions=True,
                        on_prev=on_prev, on_next=on_next, on_like=on_like, on_add_playlist=on_add)
        side_label = 'Side A: Similar' if st.session_state.current_side == 'A' else 'Side B: Explore'
        if st.button(side_label, key='side_toggle'):
            st.session_state.current_side = 'B' if st.session_state.current_side == 'A' else 'A'
            st.session_state.recommendations = st.session_state.side_b if st.session_state.current_side == 'B' else st.session_state.side_a
            st.session_state.current_rec_index = 0
            st.rerun()
