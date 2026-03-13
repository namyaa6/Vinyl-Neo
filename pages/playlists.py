import streamlit as st

st.set_page_config(layout="wide", page_title="Playlists - Vinyl Neo")

# Initialize session state
if 'custom_playlists' not in st.session_state:
    st.session_state.custom_playlists = {}
if 'liked_songs' not in st.session_state:
    st.session_state.liked_songs = []

st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton > button {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #e74c3c;
        border-color: #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

# Home button
col_home, col_space = st.columns([1, 20])
with col_home:
    if st.button('🏠', key='home_btn'):
        st.session_state.started = False
        st.switch_page("app.py")

st.markdown('<h1 style="text-align: center; font-size: 3rem;">📚 MY PLAYLISTS</h1>', unsafe_allow_html=True)

# Create new playlist
st.markdown('---')
st.subheader('➕ Create New Playlist')

col1, col2 = st.columns([3, 1])
with col1:
    new_playlist_name = st.text_input('Playlist Name', placeholder='Enter playlist name...', label_visibility='collapsed')
with col2:
    if st.button('Create', use_container_width=True):
        if new_playlist_name and new_playlist_name not in st.session_state.custom_playlists:
            st.session_state.custom_playlists[new_playlist_name] = []
            st.success(f'✅ Created playlist: {new_playlist_name}')
            st.rerun()

# Display Liked Songs
st.markdown('---')
st.markdown('### ❤️ Liked Songs')

if st.session_state.liked_songs:
    for i, song in enumerate(st.session_state.liked_songs, 1):
        col1, col2, col3 = st.columns([1, 5, 1])
        with col1:
            st.write(f"**{i}.**")
        with col2:
            st.write(f"**{song['name']}** - {song['artist']} ({song['genre']})")
        with col3:
            if st.button('🗑️', key=f'del_liked_{i}'):
                st.session_state.liked_songs.pop(i-1)
                st.rerun()
else:
    st.info('No liked songs yet. Start searching and liking songs!')

# Display Custom Playlists
st.markdown('---')
st.markdown('### 🎵 Custom Playlists')

if st.session_state.custom_playlists:
    for playlist_name, songs in st.session_state.custom_playlists.items():
        with st.expander(f'📚 {playlist_name} ({len(songs)} songs)'):
            if songs:
                for i, song in enumerate(songs, 1):
                    st.write(f"{i}. {song}")
            else:
                st.info('No songs in this playlist yet.')
            
            if st.button(f'Delete Playlist', key=f'del_playlist_{playlist_name}'):
                del st.session_state.custom_playlists[playlist_name]
                st.rerun()
else:
    st.info('No custom playlists yet. Create one above!')