import streamlit as st

st.set_page_config(layout="wide", page_title="About - Vinyl Neo")

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">ABOUT VINYL NEO</h1>', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    ### About This Project

    **Vinyl Neo** is an AI-powered music discovery tool with an analog soul. Unlike generic streaming apps, it leans into vinyl-inspired UX and explainable ML.

    - **Content-based filtering** (cosine similarity on audio features)
    - **Spotify integration** for recommendations and 30s previews
    - **Side A / Side B** – similar picks vs. exploration
    - **Discover** – browse by genre and themed crates
    - **Mood-based** recommendations with contrast (match mood, shift brighter, lean in)
    - **Feature playground** – tune energy, valence, danceability
    - **Playlists** and **Liked Songs** with previews and Open in Spotify
    - **Remix** – sequence 3–4 tracks with preview players

    ### Built With

    - Python, Streamlit, scikit-learn
    - Spotify Web API
    - 114,000+ track dataset

    ---
    Developed as a music lab and recommendation system.
    """)

st.markdown('<br>', unsafe_allow_html=True)
if st.button('Back to menu'):
    st.session_state.started = True
    st.switch_page("app.py")
