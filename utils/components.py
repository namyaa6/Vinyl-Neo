"""Shared UI components for Vinyl Neo."""
import streamlit as st


@st.cache_data(ttl=3600)
def enrich_rec_with_spotify(track_name: str, artist_name: str, track_id=None) -> dict | None:
    """Fetch album art, preview, and external URL from Spotify. Returns dict or None."""
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        if not spotify._client_id:
            return None
        q = f"{track_name} {artist_name}" if track_name and artist_name else str(track_name or artist_name)
        items = spotify.search_track(q, limit=3)
        for track in items:
            sim = SpotifyService.simplify_track(track)
            if sim.get("preview_url") or sim.get("image_url") or sim.get("external_url"):
                return {
                    "image_url": sim.get("image_url"),
                    "preview_url": sim.get("preview_url"),
                    "external_url": sim.get("external_url"),
                }
    except Exception:
        pass
    return None


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

    img_url = str(image_url).strip() if image_url else ""
    if img_url and img_url.startswith("http"):
        img_html = (
            f'<img src="{img_url}" style="width: 200px; height: 200px; border-radius: 50%; '
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

    preview_str = str(preview_url).strip() if preview_url is not None else ""
    if preview_str and preview_str.startswith("http"):
        st.audio(preview_str)

    # Ensure external_url is a valid URL string (avoid st.link_button compatibility issues)
    url_str = str(external_url).strip() if external_url is not None else ""
    if url_str and url_str.startswith("http") and "nan" not in url_str.lower():
        st.markdown(
            f'<a href="{url_str}" target="_blank" rel="noopener noreferrer" '
            'style="display:inline-block;padding:0.5rem 1rem;background:#2c1810;color:#c4a574;'
            'border:1px solid #4a3728;border-radius:8px;text-decoration:none;margin-top:0.5rem;">'
            "Open in Spotify</a>",
            unsafe_allow_html=True,
        )

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
