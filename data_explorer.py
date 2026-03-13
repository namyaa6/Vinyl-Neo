import pandas as pd
import config as Config

def explore_spotify_data():
    try:
        df = pd.read_csv(r'D:\Projects2025\song_recommendation\data\raw\spotify_tracks.csv')
        print(f"loaded {len(df)} tracks \n")
        print(f"total columns {len(df.columns)}")
    except FileNotFoundError:
        print("error...file not found!")
        return

    print("\n track songs")
    print(df[['track_name', 'artists', 'popularity']].head(10))

    print("\n columns")
    print(list(df.columns))

    print("\n features")
    features = ['danceability','energy', 'valence','tempo']
    print(df[features].describe())

    print("\n data types")
    print(df.dtypes)


if __name__ == "__main__":
    explore_spotify_data()    