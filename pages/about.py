import streamlit as st

st.set_page_config(layout="wide", page_title="About - Vinyl Neo")

if "about_section" not in st.session_state:
    st.session_state.about_section = None

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .about-contact a { color: #c4a574; text-decoration: none; }
    .about-contact a:hover { text-decoration: underline; }
    .about-content-box {
        background: #141010;
        border: 1px solid #2c1810;
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin: 2rem auto;
        max-width: 720px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        border-left: 4px solid #c4a574;
    }
    .about-content-box h3 { color: #c4a574; margin-top: 0; }
    .about-content-box ul { margin: 0.5rem 0; padding-left: 1.5rem; line-height: 1.7; }
    .about-content-box p { line-height: 1.7; margin-bottom: 1rem; }
    section.main [data-testid="column"] .stButton > button {
        min-height: 140px !important;
        background: #141010 !important;
        color: #c4a574 !important;
        border: 2px solid #2c1810 !important;
        border-radius: 16px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.3s !important;
        white-space: pre-line !important;
        line-height: 1.5 !important;
        text-decoration: none !important;
    }
    section.main [data-testid="column"] .stButton > button::first-line {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
    }
    section.main [data-testid="column"] .stButton > button:hover {
        border-color: #c4a574 !important;
        background: #1a1510 !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
        color: #c4a574 !important;
    }
    section.main [data-testid="column"] .stButton > button[kind="primary"] {
        border-color: #c4a574 !important;
        box-shadow: 0 0 24px rgba(196,165,116,0.25) !important;
        background: #1a1510 !important;
        color: #c4a574 !important;
    }
</style>
""", unsafe_allow_html=True)

if st.button('Back to menu', key='back_menu'):
    st.session_state.started = True
    st.switch_page("app.py")

st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">ABOUT VINYL NEO</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; margin-bottom: 2rem;">Choose a section to explore</p>', unsafe_allow_html=True)

# Two card-style buttons – two lines each, different font sizes (NOT links)
_, col_left, col_right, _ = st.columns([1, 2, 2, 1])

with col_left:
    if st.button(
        "About This Project",
        key="btn_about_project",
        use_container_width=True,
        type="primary" if st.session_state.about_section == "project" else "secondary",
    ):
        st.session_state.about_section = "project"
        st.rerun()

with col_right:
    if st.button(
        "About Me",
        key="btn_about_me",
        use_container_width=True,
        type="primary" if st.session_state.about_section == "me" else "secondary",
    ):
        st.session_state.about_section = "me"
        st.rerun()

# Content box below - centered, larger, theme-styled
if st.session_state.about_section:
    if st.session_state.about_section == "me":
        content = """
        <h3 style="color: #c4a574; margin-top: 0;">About Me</h3>
        <p>I'm <strong>Namya Jain</strong>, a second-year BTech student in Artificial Intelligence and Machine Learning at Indira Gandhi Delhi Technical University for Women. A music enthusiast who loves to laugh through life while sipping tea.</p>
        <p>This project connects me to one thing I love adding while doing anything: listening to music. Whether it's going for a walk, tidying up my room, studying or working—one thing that always stays constant is my earphones paired with Spotify, vibing to my favourite collection of songs.</p>
        <p>For me, music changes my perspective. If there's something I would have to do that I hate, I would procrastinate and delay it a lot—but if I pair it with music, voilà, you get that work done in an hour. This project is quite special to me, and I hope you resonate with the same feeling.</p>
        <p class="about-contact"><strong>Contact:</strong> <a href="mailto:namyajain6@gmail.com">namyajain6@gmail.com</a></p>
        """
    else:
        content = """
        <h3 style="color: #c4a574; margin-top: 0;">About This Project</h3>
        <p><strong>Vinyl Neo</strong> is an AI-powered music discovery app that blends Spotify's catalog with local machine learning to surface familiar tracks and new favorites.</p>
        <p><strong>Features</strong></p>
        <ul>
        <li><strong>Search</strong> – Spotify-first search; any track on Spotify can seed recommendations</li>
        <li><strong>Discover</strong> – Genre vinyls and themed crates (Chill Lo-Fi, Late Night Jazz, Electronic Dreams, etc.)</li>
        <li><strong>Mood</strong> – Mood-based recommendations with contrast modes (match mood, shift brighter, lean in)</li>
        <li><strong>Playground</strong> – Tune energy, valence, danceability, and tempo for targeted recommendations</li>
        <li><strong>Playlists & Liked Songs</strong> – Save tracks with 30s previews and "Open in Spotify"; persisted locally across refresh</li>
        <li><strong>Remix</strong> – Chain 3–4 tracks into a short "side" with preview players</li>
        <li><strong>Side A / Side B</strong> (Search) – Similar picks vs. exploration recommendations</li>
        </ul>
        <p><strong>Tech Stack</strong></p>
        <ul>
        <li>Python, Streamlit, pandas, scikit-learn (cosine similarity on audio features)</li>
        <li>Spotify Web API (Client Credentials flow): search, recommendations, 30s previews, album art</li>
        <li>114k+ track local dataset for ML fallback when Spotify is unavailable</li>
        <li>Local JSON persistence for liked songs and playlists</li>
        </ul>
        """

    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.markdown(
            '<div id="about-content" class="about-content-box">' + content + "</div>",
            unsafe_allow_html=True,
        )

    # Scroll to content after click so user doesn't need to scroll
    st.html(
        """<script>
            (function() {
                var el = document.getElementById('about-content');
                if (el) setTimeout(function(){ el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 100);
            })();
        </script>""",
        unsafe_allow_javascript=True
    )
