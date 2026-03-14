import os
from dotenv import load_dotenv
load_dotenv()


def _get_spotify_creds(key: str) -> str:
    """Read from st.secrets (Streamlit Cloud) or os.environ (local .env)."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            val = st.secrets.get(key, '')
            if val:
                return str(val)
    except Exception:
        pass
    return os.getenv(key, '')


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
