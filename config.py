import os
from dotenv import load_dotenv
load_dotenv()


def _get_spotify_creds(key: str) -> str:
    """Read from os.environ (.env) or st.secrets (Streamlit Cloud)."""
    val = os.getenv(key, '').strip()
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            # Top-level keys: SPOTIFY_CLIENT_ID = "xxx"
            val = st.secrets.get(key, '') or getattr(st.secrets, key, '')
            if val:
                return str(val).strip()
            # Section [spotify]: client_id / SPOTIFY_CLIENT_ID
            sec = st.secrets.get('spotify') or getattr(st.secrets, 'spotify', None)
            if sec:
                alt = key.replace('SPOTIFY_', '').lower()  # client_id, client_secret
                val = sec.get(key) or sec.get(alt) or getattr(sec, key, '') or getattr(sec, alt, '')
                if val:
                    return str(val).strip()
    except Exception:
        pass
    return ''


class Config:
    # Uses st.secrets on Streamlit Cloud, else .env locally
    SPOTIFY_CLIENT_ID = _get_spotify_creds('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = _get_spotify_creds('SPOTIFY_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://vinyl-neo.streamlit.app/')

    SPOTIFY_SCOPE = (
        'user-library-read '
        'user-top-read '
        'playlist-modify-public '
        'playlist-modify-private '
        'user-read-playback-state '
        'user-modify-playback-state '
        'user-read-recently-played'
    )
    
    # Folder paths
    DATA_DIR = 'data'
    RAW_DATA_DIR = 'data/raw'
    PROCESSED_DATA_DIR = 'data/processed'
    MODELS_DIR = 'models'
    
    # Recommendation settings
    N_RECOMMENDATIONS = 10
    MIN_SIMILARITY_SCORE = 0.6
    
    # Audio features for recommendations
    AUDIO_FEATURES = [
        'danceability', 'energy', 'loudness', 'speechiness',
        'acousticness', 'instrumentalness', 'valence', 'tempo'
    ]


# Test when running directly
if __name__ == "__main__":
    print("\n=== Configuration Test ===\n")
    
    if Config.SPOTIFY_CLIENT_ID:
        print("Spotify credentials found")
    else:
        print("No Spotify credentials (that's OK for now)")
    
    print(f"Will recommend {Config.N_RECOMMENDATIONS} songs")
    print(f"Using {len(Config.AUDIO_FEATURES)} audio features")
    print("\nReady to go!")
