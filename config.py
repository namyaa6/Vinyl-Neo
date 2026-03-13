import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Existing Spotify config...
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')
    
    # Last.fm config
    LASTFM_API_KEY = os.getenv('LASTFM_API_KEY', '')
    LASTFM_API_SECRET = os.getenv('LASTFM_API_SECRET', '')
    
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
