"""Persist liked songs and playlists across page refreshes."""
import json
import os

_USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "user_data.json")


def ensure_user_session_loaded(st_session_state):
    """Load user data into session state if not yet loaded."""
    if "_user_data_loaded" not in st_session_state:
        data = load_user_data()
        st_session_state.liked_songs = data.get("liked_songs", [])
        st_session_state.custom_playlists = data.get("custom_playlists", {})
        st_session_state.playlist_queue = data.get("playlist_queue", [])
        st_session_state._user_data_loaded = True


def _ensure_data_dir():
    d = os.path.dirname(_USER_DATA_PATH)
    if d and not os.path.exists(d):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError:
            pass


def load_user_data():
    """Load liked_songs, custom_playlists, playlist_queue from JSON file."""
    try:
        if os.path.exists(_USER_DATA_PATH):
            with open(_USER_DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {"liked_songs": [], "custom_playlists": {}, "playlist_queue": []}


def save_user_data(liked_songs, custom_playlists, playlist_queue):
    """Save to JSON file. Fails silently if unwritable (e.g. Streamlit Cloud)."""
    try:
        _ensure_data_dir()
        data = {
            "liked_songs": liked_songs,
            "custom_playlists": custom_playlists,
            "playlist_queue": playlist_queue,
        }
        with open(_USER_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except (OSError, TypeError):
        pass
