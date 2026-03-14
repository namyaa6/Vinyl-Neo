"""Shared UI components for Vinyl Neo."""
import streamlit as st


def _normalize_rec(rec):
    """Normalize rec dict to common keys for display."""
    return {
        "track_name": rec.get("track_name") or rec.get("name", "Unknown"),
        "artist": rec.get("artist") or rec.get("artists", ""),
        "genre": rec.get("genre") or rec.get("track_genre", ""),
        "preview_url": rec.get("preview_url"),
        "image_url": rec.get("image_url"),
        "external_url": rec.get("external_url"),
    }


def render_rec_card(
    rec,
    df=None,
    key_prefix="rec",
    show_actions=True,
    on_prev=None,
    on_next=None,
    on_like=None,
    on_add_playlist=None,
):
    """
    Render a single recommendation card: vinyl-style with album art, track name, artist,
    30s preview, Open in Spotify link, and optional action buttons.

    rec: dict with track_name/name, artist/artists, optional preview_url, image_url, external_url, genre
    df: optional dataframe (for future use, e.g. local art lookup)
    key_prefix: unique key prefix for Streamlit widgets
    show_actions: whether to show prev/like/add to playlist/next buttons
    on_prev, on_next, on_like, on_add_playlist: callables with no args, called when button clicked
    """
    n = _normalize_rec(rec)
    track_name = n["track_name"]
    artist = n["artist"]
    genre = n["genre"]
    preview_url = n["preview_url"]
    image_url = n["image_url"]
    external_url = n["external_url"]

    if image_url:
        img_html = (
            f'<img src="{image_url}" style="width: 200px; height: 200px; border-radius: 50%; '
            'object-fit: cover; border: 6px solid #2c1810;">'
        )
    else:
        img_html = (
            '<div class="rotating-album" style="width: 200px; height: 200px; '
            'border-radius: 50%; border: 8px solid #2c1810; '
            'background: radial-gradient(circle, #1a1a1a 0%, #000 70%); margin: 0 auto; '
            'position: relative;"></div>'
        )

    meta = f"{artist} · {genre}" if genre else artist
    st.markdown(
        f"""
        <div class="rec-card">
            {img_html}
            <div class="song-title">{track_name}</div>
            <div class="song-meta">{meta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if preview_url:
        st.audio(preview_url)

    if external_url:
        st.link_button("Open in Spotify", url=external_url, type="secondary", key=f"{key_prefix}_spotify")

    if show_actions and (on_prev is not None or on_next is not None or on_like is not None or on_add_playlist is not None):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if on_prev is not None and st.button("← Previous", key=f"{key_prefix}_prev", use_container_width=True):
                on_prev()
        with c2:
            if on_like is not None and st.button("♥ Like", key=f"{key_prefix}_like", use_container_width=True):
                on_like()
        with c3:
            if on_add_playlist is not None and st.button(
                "Add to Playlist", key=f"{key_prefix}_add", use_container_width=True
            ):
                on_add_playlist()
        with c4:
            if on_next is not None and st.button("Next →", key=f"{key_prefix}_next", use_container_width=True):
                on_next()
