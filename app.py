# app.py - Home Page

import streamlit as st
import pandas as pd

from utils.user_data import ensure_user_session_loaded

st.set_page_config(
    page_title="Vinyl Neo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_data():
    return pd.read_csv('data/raw/spotify_tracks.csv')

df = load_data()

if 'started' not in st.session_state:
    st.session_state.started = False
ensure_user_session_loaded(st.session_state)

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .vinyl-container { position: fixed; right: -15%; top: 10%; z-index: 0; }
    .vinyl { width: 600px; height: 600px; background: radial-gradient(circle, #1a1a1a 0%, #000 70%, #1a1a1a 100%);
        border-radius: 50%; border: 2px solid #2c1810; box-shadow: 0 0 50px rgba(0,0,0,0.9);
        animation: spin 10s linear infinite; position: relative; }
    .vinyl::before { content: ''; position: absolute; width: 100px; height: 100px; background: #c4a574;
        border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); }
    .vinyl::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; border-radius: 50%;
        background: repeating-radial-gradient(circle, transparent 0, transparent 5px, rgba(255,255,255,0.03) 6px); }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .welcome-box { position: relative; z-index: 1; margin-top: 20vh; margin-left: 5vw; max-width: 500px; }
    .main-title { font-size: 5rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 0; }
    .accent { color: #c4a574; }
    .btn-card { width: 100%; min-height: 120px; background: #141010 !important; color: #f5e6d3 !important;
        border: 1px solid #2c1810 !important; border-radius: 16px !important; font-size: 1.15rem !important;
        font-weight: bold !important; padding: 1.25rem 1rem !important; transition: all 0.3s !important;
        display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important;
        gap: 0.35rem !important; text-align: center !important; line-height: 1.3 !important; }
    .btn-card:hover { border-color: #c4a574 !important; transform: translateY(-4px); background: #1a1510 !important; box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important; }
    .btn-card .btn-title { font-size: 1.35rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; margin-bottom: 0.25rem !important; }
    .btn-card .btn-desc { font-size: 0.95rem !important; font-weight: 500 !important; color: #c4a574 !important; opacity: 0.9 !important; }
    section.main .block-container .stButton { width: 100%; }
    .stButton > button { white-space: pre-line !important; }
    section.main .stButton > button { width: 100% !important; min-height: 120px !important; white-space: pre-line !important;
        border-radius: 16px !important; background: #141010 !important; color: #f5e6d3 !important; border: 2px solid #2c1810 !important;
        font-size: 1.15rem !important; font-weight: bold !important; padding: 1.25rem 1rem !important;
        display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important;
        gap: 0.35rem !important; text-align: center !important; line-height: 1.4 !important; transition: all 0.3s !important; }
    section.main .stButton > button:hover { border-color: #c4a574 !important; transform: translateY(-4px); background: #1a1510 !important; box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.started:
    st.markdown("""
    <div class="vinyl-container"><div class="vinyl"></div></div>
    <div class="welcome-box">
        <h1 class="main-title">VINYL <span class="accent">NEO</span></h1>
        <p style="font-size: 1.5rem; color: #888;">AI-Powered Discovery. Analog Soul.</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("GET STARTED", use_container_width=True):
            st.session_state.started = True
            st.rerun()
else:
    st.markdown('<h1 style="text-align: center; margin-top: 1rem;">Welcome to VINYL NEO</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #888; margin-bottom: 1.5rem;">AI-Powered Discovery. Analog Soul.</p>', unsafe_allow_html=True)

    # Row 1: SEARCH, DISCOVER, PLAYLISTS
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("SEARCH\nFind songs & artists", key="search_card", use_container_width=True):
            st.switch_page("pages/search.py")
    with col2:
        if st.button("DISCOVER\nBrowse by genre", key="discover_card", use_container_width=True):
            st.switch_page("pages/discover.py")
    with col3:
        if st.button("PLAYLISTS\nYour saved music", key="playlist_card", use_container_width=True):
            st.switch_page("pages/playlists.py")

    # Row 2: MOOD, PLAYGROUND, ABOUT
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("MOOD\nMusic by mood", key="mood_card", use_container_width=True):
            st.switch_page("pages/mood.py")
    with col5:
        if st.button("PLAYGROUND\nTune audio features", key="playground_card", use_container_width=True):
            st.switch_page("pages/playground.py")
    with col6:
        if st.button("ABOUT\nAbout this project", key="about_card", use_container_width=True):
            st.switch_page("pages/about.py")
