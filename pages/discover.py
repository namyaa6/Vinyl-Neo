import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from services.lastfm_service import LastFMService

lastfm = LastFMService()

st.set_page_config(layout="wide", page_title="Discover - Vinyl Neo")

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

# Initialize session state
if 'genre_recommendations' not in st.session_state:
    st.session_state.genre_recommendations = []
if 'current_genre_rec_index' not in st.session_state:
    st.session_state.current_genre_rec_index = 0

st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .clickable-vinyl {
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, #1a1a1a 0%, #000 80%);
        border-radius: 50%;
        border: 3px solid #e74c3c;
        margin: 0 auto 1rem;
        position: relative;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    
    .clickable-vinyl:hover {
        transform: scale(1.15);
        box-shadow: 0 0 40px rgba(231, 76, 60, 0.6);
    }
    
    .clickable-vinyl::after {
        content: '';
        position: absolute;
        width: 50px;
        height: 50px;
        background: #0a0a0a;
        border: 2px solid #333;
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    .genre-label {
        text-align: center;
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }
    
    .stButton > button {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Home button
col_home, col_space = st.columns([1, 20])
with col_home:
    if st.button('🏠', key='home_btn'):
        st.session_state.started = False
        st.switch_page("app.py")

st.markdown('<h1 style="text-align: center; font-size: 3rem; margin-bottom: 1rem;">🎵 DISCOVER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; font-size: 1.2rem; margin-bottom: 3rem;">Explore music by genre</p>', unsafe_allow_html=True)

# Famous genres with audio features
genres = [
    'acoustic', 'pop', 'rock', 'jazz',
    'hip-hop', 'electronic', 'classical', 'indie',
    'blues', 'metal', 'folk', 'dance'
]

# Function to get recommendations for genre
def get_genre_recommendations(genre):
    """Get genre recommendations from both local cosine similarity and Last.fm"""
    
    # 1. Local ML-based recommendations (your existing logic)
    genre_songs = df[df['track_genre'].str.contains(genre, case=False, na=False)]
    local_recs = []
    
    if len(genre_songs) > 0:
        sample_idx = genre_songs.sample(1).index[0]
        song_features = feature_matrix[sample_idx].reshape(1, -1)
        similarities = cosine_similarity(song_features, feature_matrix)[0]
        
        similar_indices = similarities.argsort()[::-1]
        
        for idx in similar_indices:
            if genre.lower() in df.iloc[idx]['track_genre'].lower():
                local_recs.append(idx)
                if len(local_recs) >= 20:
                    break
    
    # 2. Last.fm genre/tag recommendations
    lastfm_tracks_simple = []
    try:
        lastfm_tracks = lastfm.get_top_tracks_by_tag(genre, limit=20)
        for track in lastfm_tracks:
            lastfm_tracks_simple.append({
                'name': track['name'],
                'artist': track['artist']['name'],
                'source': 'lastfm'
            })
    except Exception:
        # If Last.fm fails, just fall back to local
        lastfm_tracks_simple = []
    
    # Return both: keep your existing index list for navigation,
    # and optionally the Last.fm metadata if you want to show it later.
    return local_recs, lastfm_tracks_simple

# Display genres in grid
cols = st.columns(4)
for i, genre in enumerate(genres):
    with cols[i % 4]:
        st.markdown(f'<div class="genre-label">{genre.upper()}</div>', unsafe_allow_html=True)
        
        # Vinyl disc as button
        if st.button(f'vinyl_{genre}', key=f'btn_{genre}', use_container_width=True):
            with st.spinner(f'Finding {genre} recommendations...'):
                local_recs, lastfm_recs = get_genre_recommendations(genre)
                if local_recs:
                    st.session_state.genre_recommendations = local_recs
                    st.session_state.current_genre_rec_index = 0
                    st.session_state.selected_genre = genre
                    # Optionally store Last.fm results for later display:
                    st.session_state.lastfm_genre_recs = lastfm_recs
                    st.rerun()

        
        st.markdown(f'<div class="clickable-vinyl"></div>', unsafe_allow_html=True)

# Display genre recommendations
if st.session_state.genre_recommendations:
    st.markdown('---')
    st.markdown(f'<h2 style="text-align: center;">🎵 {st.session_state.selected_genre.upper()} RECOMMENDATIONS</h2>', unsafe_allow_html=True)
    
    idx = st.session_state.genre_recommendations[st.session_state.current_genre_rec_index]
    rec = df.iloc[idx]
    
    col1, col_main, col3 = st.columns([1, 2, 1])
    
    with col_main:
        st.markdown(f"""
        <div style="background: #111111; padding: 40px; border-radius: 25px; text-align: center; border: 1px solid #222;">
            <div style="width: 300px; height: 300px; border-radius: 50%; border: 10px solid #1a1a1a; 
                 background: radial-gradient(circle, #1a1a1a 0%, #000000 70%, #1a1a1a 100%); 
                 margin: 0 auto; position: relative;">
                <div style="position: absolute; width: 80px; height: 80px; background: #e74c3c; 
                     border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%);"></div>
            </div>
            <div style="font-size: 2rem; font-weight: bold; margin-top: 20px; color: #ffffff;">{rec['track_name']}</div>
            <div style="color: #e74c3c; font-size: 1.1rem; margin-top: 10px;">{rec['artists']} • {rec['track_genre']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Previous", use_container_width=True, key='genre_prev'):
                if st.session_state.current_genre_rec_index > 0:
                    st.session_state.current_genre_rec_index -= 1
                    st.rerun()
        with c2:
            if st.button("Next ➡️", use_container_width=True, key='genre_next'):
                if st.session_state.current_genre_rec_index < len(st.session_state.genre_recommendations) - 1:
                    st.session_state.current_genre_rec_index += 1
                    st.rerun()

if 'lastfm_genre_recs' in st.session_state and st.session_state.lastfm_genre_recs:
    st.markdown('---')
    st.markdown(
        f'<h3 style="text-align: center; color: #888;">More {st.session_state.selected_genre.upper()} from Last.fm</h3>',
        unsafe_allow_html=True
    )
    for t in st.session_state.lastfm_genre_recs[:10]:
        st.write(f"- {t['name']} — {t['artist']} (Last.fm)")
