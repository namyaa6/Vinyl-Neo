# app.py - Home Page

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Vinyl Neo", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/raw/spotify_tracks.csv')

df = load_data()

# Initialize session state
if 'started' not in st.session_state:
    st.session_state.started = False

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3/4 Vinyl Positioning */
    .vinyl-container {
        position: fixed;
        right: -15%;
        top: 10%;
        z-index: 0;
    }

    .vinyl {
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, #1a1a1a 0%, #000000 70%, #1a1a1a 100%);
        border-radius: 50%;
        border: 2px solid #333;
        box-shadow: 0 0 50px rgba(0,0,0,0.9);
        animation: spin 10s linear infinite;
        position: relative;
    }

    .vinyl::before {
        content: '';
        position: absolute;
        width: 100px;
        height: 100px;
        background: #e74c3c;
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 0 20px rgba(231, 76, 60, 0.5);
    }

    .vinyl::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        border-radius: 50%;
        background: repeating-radial-gradient(circle, transparent 0, transparent 5px, rgba(255,255,255,0.03) 6px);
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .welcome-box {
        position: relative;
        z-index: 1;
        margin-top: 20vh;
        margin-left: 5vw;
        max-width: 500px;
    }

    .main-title {
        font-size: 5rem;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 0;
    }

    .accent { color: #e74c3c; }
    
    .stButton > button {
        background-color: #e74c3c;
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 1rem 3rem;
        border: none;
        border-radius: 50px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #c0392b;
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(231, 76, 60, 0.5);
    }
    
    .feature-card {
        background: #111111;
        padding: 2.5rem;
        border-radius: 15px;
        border: 1px solid #222;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .feature-card:hover {
        border-color: #e74c3c;
        transform: translateY(-5px);
        background: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.started:
    # Home page - before "Get Started"
    st.markdown("""
    <div class="vinyl-container">
        <div class="vinyl"></div>
    </div>

    <div class="welcome-box">
        <h1 class="main-title">VINYL <span class="accent">NEO</span></h1>
        <p style="font-size: 1.5rem; color: #888;">AI-Powered Discovery. Analog Soul.</p>
    </div>
    """, unsafe_allow_html=True)

    # Get Started button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("GET STARTED", use_container_width=True):
            st.session_state.started = True
            st.rerun()

else:
    # After "Get Started" - show features
    st.markdown('<h1 style="text-align: center; margin-top: 3rem;">Welcome to VINYL NEO</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #888; font-size: 1.2rem; margin-bottom: 3rem;">Your AI-Powered Music Discovery Platform</p>', unsafe_allow_html=True)
    
    # Three equal-sized feature cards
    st.markdown('---')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button('dummy1', key='search_card', use_container_width=True):
            st.switch_page("pages/search.py")
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 4rem;">🔍</div>
            <h2>SEARCH</h2>
            <p style="color: #888; font-size: 1.1rem;">Find any song or artist</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button('dummy2', key='discover_card', use_container_width=True):
            st.switch_page("pages/discover.py")
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 4rem;">🎵</div>
            <h2>DISCOVER</h2>
            <p style="color: #888; font-size: 1.1rem;">Explore new genres</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button('dummy3', key='playlist_card', use_container_width=True):
            st.switch_page("pages/playlists.py")
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 4rem;">📚</div>
            <h2>PLAYLISTS</h2>
            <p style="color: #888; font-size: 1.1rem;">Manage collections</p>
        </div>
        """, unsafe_allow_html=True)