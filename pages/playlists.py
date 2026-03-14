"""Playlists, Liked Songs, and Remix (crossfade-style)."""
import streamlit as st

from utils.user_data import ensure_user_session_loaded, save_user_data

st.set_page_config(layout="wide", page_title="Playlists - Vinyl Neo")

ensure_user_session_loaded(st.session_state)
if 'remix_tracks' not in st.session_state:
    st.session_state.remix_tracks = []

# Migrate old keys
if 'mixtapes' in st.session_state and st.session_state.mixtapes:
    st.session_state.custom_playlists = {**st.session_state.get('custom_playlists', {}), **st.session_state.mixtapes}
    del st.session_state['mixtapes']
if 'mixtape_queue' in st.session_state:
    st.session_state.playlist_queue = st.session_state.mixtape_queue
    del st.session_state['mixtape_queue']

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #f5e6d3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton > button { background: #2c1810; color: #c4a574; border: 1px solid #4a3728; }
    .playlist-card { background: #141010; padding: 16px; border-radius: 12px; border: 1px solid #2c1810; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

if st.button('Back to menu', key='back_menu'):
    st.session_state.started = True
    st.switch_page("app.py")

st.markdown('<h1 style="text-align: center; font-size: 2.5rem; color: #f5e6d3;">PLAYLISTS</h1>', unsafe_allow_html=True)

tab_playlists, tab_liked, tab_remix = st.tabs(["Playlists", "Liked Songs", "Remix"])

with tab_playlists:
    st.markdown('### Playlist queue')
    if st.session_state.playlist_queue:
        artists_seen = set()
        unique = []
        for t in st.session_state.playlist_queue:
            artist = t.get('artist', t.get('artists', ''))
            if artist not in artists_seen:
                artists_seen.add(artist)
                unique.append(t)
        st.session_state.playlist_queue = unique[:12]

        st.caption(f"{len(st.session_state.playlist_queue)} tracks in queue. Max one per artist.")
        pl_name = st.text_input('Playlist title', placeholder='e.g. Late Night Vibes', key='pl_name')
        pl_desc = st.text_input('Description (optional)', placeholder='Short description', key='pl_desc')
        if st.button('Create playlist', key='create_pl'):
            if pl_name and pl_name.strip():
                st.session_state.custom_playlists[pl_name.strip()] = {
                    'description': pl_desc or '',
                    'tracks': list(st.session_state.playlist_queue),
                }
                st.session_state.playlist_queue = []
                save_user_data(st.session_state.liked_songs, st.session_state.custom_playlists, st.session_state.playlist_queue)
                st.success(f'Created playlist: {pl_name}')
                st.rerun()
        if st.button('Clear queue', key='clear_queue'):
            st.session_state.playlist_queue = []
            save_user_data(st.session_state.liked_songs, st.session_state.custom_playlists, st.session_state.playlist_queue)
            st.rerun()
    else:
        st.info('Add tracks from Search or Discover to build a playlist.')

    st.markdown('### My playlists')
    if st.session_state.custom_playlists:
        for name, data in st.session_state.custom_playlists.items():
            tracks = data.get('tracks', [])
            with st.expander(f'{name} ({len(tracks)} tracks)'):
                if data.get('description'):
                    st.caption(data['description'])
                for i, t in enumerate(tracks, 1):
                    title = t.get('track_name', t.get('name', 'Unknown'))
                    artist = t.get('artist', t.get('artists', ''))
                    st.write(f"{i}. {title} — {artist}")
                    if t.get('preview_url'):
                        st.audio(t['preview_url'])
                    if t.get('external_url'):
                        st.link_button('Open in Spotify', url=t['external_url'], type='secondary', key=f'pl_spot_{name}_{i}')
                if st.button(f'Delete playlist: {name}', key=f'del_pl_{name}'):
                    del st.session_state.custom_playlists[name]
                    save_user_data(st.session_state.liked_songs, st.session_state.custom_playlists, st.session_state.playlist_queue)
                    st.rerun()
    else:
        st.info('No playlists yet.')

with tab_liked:
    st.markdown('### Liked Songs')
    if st.session_state.liked_songs:
        for i, song in enumerate(st.session_state.liked_songs, 1):
            name = song.get('name', 'Unknown')
            artist = song.get('artist', '')
            genre = song.get('genre', '')
            st.write(f"**{name}** — {artist}" + (f" ({genre})" if genre else ""))
            if song.get('preview_url'):
                st.audio(song['preview_url'])
            if song.get('external_url'):
                st.link_button('Open in Spotify', url=song['external_url'], type='secondary', key=f'liked_spot_{i}')
            if st.button('Remove', key=f'del_liked_{i}'):
                st.session_state.liked_songs.pop(i - 1)
                save_user_data(st.session_state.liked_songs, st.session_state.custom_playlists, st.session_state.playlist_queue)
                st.rerun()
    else:
        st.info('No liked songs yet. Like tracks from Search or Discover.')

with tab_remix:
    st.markdown('### Remix (3–4 tracks)')
    st.caption('Pick 3–4 tracks to play in sequence. Uses Spotify 30s previews.')
    pool = list(st.session_state.playlist_queue)
    for s in st.session_state.liked_songs:
        pool.append({
            'name': s.get('name'),
            'artist': s.get('artist'),
            'genre': s.get('genre', ''),
            'preview_url': s.get('preview_url'),
            'external_url': s.get('external_url'),
        })
    for name, data in st.session_state.custom_playlists.items():
        for t in data.get('tracks', []):
            pool.append({
                'name': t.get('track_name', t.get('name')),
                'artist': t.get('artist', t.get('artists', '')),
                'genre': t.get('genre', ''),
                'preview_url': t.get('preview_url'),
                'external_url': t.get('external_url'),
            })
    if pool:
        labels = [f"{t.get('name', t.get('track_name', '?'))} — {t.get('artist', '')}" for t in pool]
        sel = st.multiselect('Tracks for remix (pick 3–4)', range(len(pool)), format_func=lambda i: labels[i], max_selections=4, key='remix_sel')
        if len(sel) >= 3 and st.button('Build remix', key='build_remix'):
            st.session_state.remix_tracks = [pool[i] for i in sel]
            st.rerun()
    else:
        st.info('Add liked songs or playlist tracks first.')

    if st.session_state.remix_tracks:
        st.markdown('**Your remix** (play in order)')
        for i, t in enumerate(st.session_state.remix_tracks, 1):
            title = t.get('name', t.get('track_name', 'Unknown'))
            artist = t.get('artist', t.get('artists', ''))
            st.markdown(f"**Segment {i}:** {title} — {artist}")
            if t.get('preview_url'):
                st.audio(t['preview_url'], key=f'remix_audio_{i}')
            if t.get('external_url'):
                st.link_button('Open in Spotify', url=t['external_url'], type='secondary', key=f'remix_spot_{i}')
        if st.button('Clear remix', key='clear_remix'):
            st.session_state.remix_tracks = []
            st.rerun()
