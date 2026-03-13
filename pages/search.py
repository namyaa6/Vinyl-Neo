import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from services.lastfm_service import LastFMService

lastfm = LastFMService()

st.set_page_config(layout="wide", page_title="Search - Vinyl Neo")

# Load data
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
if 'current_rec_index' not in st.session_state:
    st.session_state.current_rec_index = 0
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'liked_songs' not in st.session_state:
    st.session_state.liked_songs = []

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Home button at top */
    .home-button {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 999;
        font-size: 2rem;
        cursor: pointer;
        transition: transform 0.3s;
    }
    
    .home-button:hover {
        transform: scale(1.2);
    }
    
    .rec-card {
        background: #111111;
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        border: 1px solid #222;
        margin-top: 2rem;
    }
    
    .rotating-album {
        width: 300px;
        height: 300px;
        border-radius: 50%;
        border: 10px solid #1a1a1a;
        background: radial-gradient(circle, #1a1a1a 0%, #000000 70%, #1a1a1a 100%);
        margin: 0 auto;
        position: relative;
        animation: spin 8s linear infinite;
    }
    
    .rotating-album::after {
        content: '';
        position: absolute;
        width: 80px;
        height: 80px;
        background: #e74c3c;
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .song-title { 
        font-size: 2rem; 
        font-weight: bold; 
        margin-top: 20px; 
        color: #ffffff;
    }
    
    .song-meta { 
        color: #e74c3c; 
        font-size: 1.1rem; 
        margin-top: 10px;
    }
    
    .stButton > button {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #e74c3c;
        border-color: #e74c3c;
    }
    
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333;
        font-size: 1.1rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Home button
col_home, col_space = st.columns([1, 20])
with col_home:
    if st.button('🏠', key='home_btn'):
        st.session_state.started = False
        st.switch_page("app.py")

# Header
st.markdown('<h1 style="text-align: center; font-size: 3rem; margin-bottom: 2rem;">🔍 SEARCH</h1>', unsafe_allow_html=True)

# Search interface
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input('', placeholder='Search by song name or artist...', label_visibility='collapsed')

with col2:
    search_type = st.radio('', ['Song Name', 'Artist Name'], horizontal=True, label_visibility='collapsed')

# Search button
if st.button('🔍 SEARCH', use_container_width=True):
    if search_query:
        with st.spinner('Finding recommendations...'):
            if search_type == 'Song Name':
                matches = df[df['track_name'].str.contains(search_query, case=False, na=False)]
            else:
                matches = df[df['artists'].str.contains(search_query, case=False, na=False)]
            
            if len(matches) > 0:
                song_idx = matches.index[0]
                song_features = feature_matrix[song_idx].reshape(1, -1)
                similarities = cosine_similarity(song_features, feature_matrix)[0]
                
                similar_indices = similarities.argsort()[::-1][1:]
                seen_songs = set()
                unique_indices = []
                
                for idx in similar_indices:
                    song_name = df.iloc[idx]['track_name'].lower().strip()
                    if song_name not in seen_songs:
                        seen_songs.add(song_name)
                        unique_indices.append(idx)
                        if len(unique_indices) >= 20:
                            break
                
                st.session_state.recommendations = unique_indices
                st.session_state.current_rec_index = 0
                st.success(f'✅ Found {len(unique_indices)} recommendations!')
            else:
                st.error('❌ No results found.')

# Display recommendations
if st.session_state.recommendations:
    idx = st.session_state.recommendations[st.session_state.current_rec_index]
    rec = df.iloc[idx]
    
    st.markdown('---')
    st.markdown(f'<h3 style="text-align: center; color: #888;">Recommendation {st.session_state.current_rec_index + 1} of {len(st.session_state.recommendations)}</h3>', unsafe_allow_html=True)
    
    col1, col_main, col3 = st.columns([1, 2, 1])
    
    with col_main:
        st.markdown(f"""
        <div class="rec-card">
            <div class="rotating-album"></div>
            <div class="song-title">{rec['track_name']}</div>
            <div class="song-meta">{rec['artists']} • {rec['track_genre']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<br>', unsafe_allow_html=True)
        st.info('🎵 Spotify preview will be available when API is integrated')
        st.markdown('<br>', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            if st.button("⬅️ Previous", use_container_width=True):
                if st.session_state.current_rec_index > 0:
                    st.session_state.current_rec_index -= 1
                    st.rerun()
        
        with c2:
            if st.button("❤️ Like", use_container_width=True):
                song_data = {
                    'name': rec['track_name'],
                    'artist': rec['artists'],
                    'genre': rec['track_genre']
                }
                if song_data not in st.session_state.liked_songs:
                    st.session_state.liked_songs.append(song_data)
                    st.success('Added to Liked Songs!')
        
        with c3:
            if st.button("➕ Queue", use_container_width=True):
                st.info('Added to queue!')
        
        with c4:
            if st.button("Next ➡️", use_container_width=True):
                if st.session_state.current_rec_index < len(st.session_state.recommendations) - 1:
                    st.session_state.current_rec_index += 1
                    st.rerun()

def get_hybrid_recommendations(track_name, artist_name, df, feature_matrix, n_local=10, n_lastfm=10):
    """Combine local ML recommendations with Last.fm similar tracks"""
    
    recommendations = []
    
    # 1. Get local content-based recommendations
    matches = df[df['track_name'].str.contains(track_name, case=False, na=False)]
    if len(matches) > 0:
        song_idx = matches.index[0]
        song_features = feature_matrix[song_idx].reshape(1, -1)
        similarities = cosine_similarity(song_features, feature_matrix)[0]
        similar_indices = similarities.argsort()[::-1][1:n_local+1]
        
        for idx in similar_indices:
            recommendations.append({
                'track_name': df.iloc[idx]['track_name'],
                'artist': df.iloc[idx]['artists'],
                'genre': df.iloc[idx]['track_genre'],
                'source': 'local_ml',
                'score': similarities[idx]
            })
    
    # 2. Get Last.fm similar tracks
    try:
        lastfm_tracks = lastfm.get_similar_tracks(track_name, artist_name, limit=n_lastfm)
        for track in lastfm_tracks:
            recommendations.append({
                'track_name': track['name'],
                'artist': track['artist']['name'],
                'genre': '',  # Last.fm doesn't return genre directly
                'source': 'lastfm',
                'score': float(track.get('match', 0))
            })
    except Exception as e:
        st.warning(f"Last.fm API error: {e}")
    
    return recommendations

# Update your search button handler
if st.button('🔍 SEARCH', use_container_width=True):
    if search_query:
        with st.spinner('Finding recommendations...'):
            if search_type == 'Song Name':
                matches = df[df['track_name'].str.contains(search_query, case=False, na=False)]
            else:
                matches = df[df['artists'].str.contains(search_query, case=False, na=False)]
            
            if len(matches) > 0:
                track_name = matches.iloc[0]['track_name']
                artist_name = matches.iloc[0]['artists']
                
                # Get hybrid recommendations
                hybrid_recs = get_hybrid_recommendations(
                    track_name, artist_name, df, feature_matrix
                )
                
                st.session_state.hybrid_recommendations = hybrid_recs
                st.session_state.current_rec_index = 0