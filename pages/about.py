import streamlit as st

st.set_page_config(layout="wide", page_title="About - Vinyl Neo")

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .about-contact a { color: #c4a574; text-decoration: none; }
    .about-contact a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

if st.button('Back to menu', key='back_menu'):
    st.session_state.started = True
    st.switch_page("app.py")

st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">ABOUT VINYL NEO</h1>', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### About Me")

    st.markdown("""
    I'm **Namya Jain**, a second-year BTech student in Artificial Intelligence and Machine Learning at Indira Gandhi Delhi Technical University for Women. A music enthusiast who loves to laugh through life while sipping tea.

    This project connects me to one thing I love adding while doing anything: listening to music. Whether it's going for a walk, tidying up my room, studying or working—one thing that always stays constant is my earphones paired with Spotify, vibing to my favourite collection of songs.

    For me, music changes my perspective. If there's something I would have to do that I hate, I would procrastinate and delay it a lot—but if I pair it with music, voilà, you get that work done in an hour. This project is quite special to me, and I hope you resonate with the same feeling.
    """)

    st.markdown(
        '<p class="about-contact"><strong>Contact:</strong> '
        '<a href="mailto:namyajain6@gmail.com">namyajain6@gmail.com</a></p>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### About This Project")

    st.markdown("""
    **Vinyl Neo** is an AI-powered music discovery app that blends Spotify's catalog with local machine learning to surface familiar tracks and new favorites.
    """)

    st.markdown("**Features**")

    st.markdown("""
    - **Search** – Spotify-first search; any track on Spotify can seed recommendations
    - **Discover** – Genre vinyls and themed crates (Chill Lo-Fi, Late Night Jazz, Electronic Dreams, etc.)
    - **Mood** – Mood-based recommendations with contrast modes (match mood, shift brighter, lean in)
    - **Playground** – Tune energy, valence, danceability, and tempo for targeted recommendations
    - **Playlists & Liked Songs** – Save tracks with 30s previews and "Open in Spotify"; persisted locally across refresh
    - **Remix** – Chain 3–4 tracks into a short "side" with preview players
    - **Side A / Side B** (Search) – Similar picks vs. exploration recommendations
    """)

    st.markdown("**Tech Stack**")

    st.markdown("""
    - Python, Streamlit, pandas, scikit-learn (cosine similarity on audio features)
    - Spotify Web API (Client Credentials flow): search, recommendations, 30s previews, album art
    - 114k+ track local dataset for ML fallback when Spotify is unavailable
    - Local JSON persistence for liked songs and playlists
    """)

