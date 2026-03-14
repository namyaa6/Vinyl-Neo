import time
import typing as t

import requests

from config import Config


class SpotifyService:
    """Lightweight wrapper around Spotify Web API using Client Credentials flow."""

    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_BASE_URL = "https://api.spotify.com/v1"

    def __init__(self) -> None:
        self._client_id = Config.SPOTIFY_CLIENT_ID
        self._client_secret = Config.SPOTIFY_CLIENT_SECRET
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    # ---- Auth helpers -------------------------------------------------
    def _fetch_token(self) -> None:
        if not self._client_id or not self._client_secret:
            raise RuntimeError(
                "Spotify client credentials are missing. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment."
            )

        response = requests.post(
            self.TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(self._client_id, self._client_secret),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self._access_token = data["access_token"]
        # expires_in is in seconds
        self._token_expires_at = time.time() + float(data.get("expires_in", 3600)) - 60

    def _get_access_token(self) -> str:
        if not self._access_token or time.time() >= self._token_expires_at:
            self._fetch_token()
        assert self._access_token is not None
        return self._access_token

    def _get_headers(self) -> dict[str, str]:
        token = self._get_access_token()
        return {"Authorization": f"Bearer {token}"}

    # ---- Core API methods ---------------------------------------------
    def search_track(self, query: str, limit: int = 5) -> list[dict]:
        """Search tracks by free‑text query."""
        params = {
            "q": query,
            "type": "track",
            "limit": limit,
        }
        response = requests.get(
            f"{self.API_BASE_URL}/search",
            headers=self._get_headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("tracks", {}).get("items", [])

    def get_recommendations_by_tracks(
        self,
        seed_track_ids: list[str],
        limit: int = 20,
        market: str | None = None,
    ) -> list[dict]:
        """Get recommended tracks based on one or more seed track IDs."""
        if not seed_track_ids:
            return []

        params: dict[str, t.Any] = {
            "seed_tracks": ",".join(seed_track_ids[:5]),
            "limit": limit,
        }
        if market:
            params["market"] = market

        response = requests.get(
            f"{self.API_BASE_URL}/recommendations",
            headers=self._get_headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("tracks", [])

    def get_recommendations_tunable(
        self,
        seed_genres: list[str] | None = None,
        seed_track_ids: list[str] | None = None,
        limit: int = 20,
        market: str | None = None,
        target_energy: float | None = None,
        target_valence: float | None = None,
        target_danceability: float | None = None,
        target_acousticness: float | None = None,
        min_tempo: float | None = None,
        max_tempo: float | None = None,
    ) -> list[dict]:
        """Get recommendations with tunable audio feature targets (for feature playground)."""
        params: dict[str, t.Any] = {"limit": limit}
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres[:5])
        if seed_track_ids:
            params["seed_tracks"] = ",".join(seed_track_ids[:5])
        if market:
            params["market"] = market
        if target_energy is not None:
            params["target_energy"] = min(1.0, max(0, target_energy))
        if target_valence is not None:
            params["target_valence"] = min(1.0, max(0, target_valence))
        if target_danceability is not None:
            params["target_danceability"] = min(1.0, max(0, target_danceability))
        if target_acousticness is not None:
            params["target_acousticness"] = min(1.0, max(0, target_acousticness))
        if min_tempo is not None:
            params["min_tempo"] = min_tempo
        if max_tempo is not None:
            params["max_tempo"] = max_tempo

        if not (seed_genres or seed_track_ids):
            return []

        response = requests.get(
            f"{self.API_BASE_URL}/recommendations",
            headers=self._get_headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("tracks", [])

    def get_recommendations_by_genres(
        self,
        seed_genres: list[str],
        limit: int = 20,
        market: str | None = None,
    ) -> list[dict]:
        """Get recommended tracks based on one or more seed genres."""
        if not seed_genres:
            return []

        params: dict[str, t.Any] = {
            "seed_genres": ",".join(seed_genres[:5]),
            "limit": limit,
        }
        if market:
            params["market"] = market

        response = requests.get(
            f"{self.API_BASE_URL}/recommendations",
            headers=self._get_headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("tracks", [])

    # ---- Convenience mappers -----------------------------------------
    @staticmethod
    def simplify_track(track: dict) -> dict:
        """Extract the main fields we care about for UI."""
        album = track.get("album", {}) or {}
        images = album.get("images") or []
        artists = track.get("artists") or []

        first_image = images[0]["url"] if images else None
        primary_artist = artists[0]["name"] if artists else ""

        return {
            "spotify_id": track.get("id"),
            "name": track.get("name"),
            "artist": primary_artist,
            "album": album.get("name"),
            "preview_url": track.get("preview_url"),
            "image_url": first_image,
            "external_url": (track.get("external_urls") or {}).get("spotify"),
        }

