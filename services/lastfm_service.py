import requests
import pylast
from config import Config

class LastFMService:
    def __init__(self):
        self.api_key = Config.LASTFM_API_KEY
        self.api_secret = Config.LASTFM_API_SECRET
        self.base_url = 'https://ws.audioscrobbler.com/2.0/'
        self.user_agent = 'VinylNeo'
        
        # Initialize pylast network (for advanced features)
        self.network = pylast.LastFMNetwork(
            api_key=self.api_key,
            api_secret=self.api_secret
        )
    
    def _make_request(self, payload):
        """Helper function for API requests"""
        headers = {'user-agent': self.user_agent}
        payload['api_key'] = self.api_key
        payload['format'] = 'json'
        response = requests.get(self.base_url, headers=headers, params=payload)
        return response.json()
    
    def get_similar_tracks(self, track_name, artist_name, limit=10):
        """Get similar tracks using track.getSimilar endpoint"""
        payload = {
            'method': 'track.getSimilar',
            'track': track_name,
            'artist': artist_name,
            'limit': limit,
            'autocorrect': 1
        }
        result = self._make_request(payload)
        
        if 'similartracks' in result:
            return result['similartracks'].get('track', [])
        return []
    
    def get_track_info(self, track_name, artist_name):
        """Get detailed track information"""
        payload = {
            'method': 'track.getInfo',
            'track': track_name,
            'artist': artist_name,
            'autocorrect': 1
        }
        return self._make_request(payload)
    
    def get_artist_similar(self, artist_name, limit=10):
        """Get similar artists"""
        payload = {
            'method': 'artist.getSimilar',
            'artist': artist_name,
            'limit': limit,
            'autocorrect': 1
        }
        result = self._make_request(payload)
        
        if 'similarartists' in result:
            return result['similarartists'].get('artist', [])
        return []
    
    def get_top_tracks_by_tag(self, tag, limit=50):
        """Get top tracks for a genre/tag"""
        payload = {
            'method': 'tag.getTopTracks',
            'tag': tag,
            'limit': limit
        }
        result = self._make_request(payload)
        
        if 'tracks' in result:
            return result['tracks'].get('track', [])
        return []
    
    def search_track(self, track_name, limit=10):
        """Search for tracks by name"""
        payload = {
            'method': 'track.search',
            'track': track_name,
            'limit': limit
        }
        result = self._make_request(payload)
        
        if 'results' in result:
            return result['results']['trackmatches'].get('track', [])
        return []
