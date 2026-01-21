import httpx
from typing import List, Dict, Any


class SpotifyService:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def get_top_tracks(self, limit: int = 50, time_range: str = "long_term") -> List[Dict[str, Any]]:
        """Fetch user's top tracks with audio features embedded"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/me/top/tracks",
                headers=self.headers,
                params={"limit": limit, "time_range": time_range}
            )
            response.raise_for_status()
            tracks = response.json()["items"]

            # Try to get audio features for each track
            for track in tracks:
                try:
                    # Attempt individual audio feature request
                    audio_response = await client.get(
                        f"{self.BASE_URL}/audio-features/{track['id']}",
                        headers=self.headers
                    )

                    if audio_response.status_code == 200:
                        track['audio_features'] = audio_response.json()
                    else:
                        # Use fallback data if audio features are restricted
                        track['audio_features'] = self._create_fallback_features(
                            track)
                except Exception:
                    # Use fallback on any error
                    track['audio_features'] = self._create_fallback_features(
                        track)

            return tracks

    def _create_fallback_features(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """Create estimated audio features when API access is restricted"""
        popularity = track.get('popularity', 50)

        return {
            'tempo': 120,
            'key': 0,
            'mode': 1,
            'time_signature': 4,
            'acousticness': 0.3,
            'energy': min(popularity / 100, 0.8)
        }

    async def get_audio_features(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """Get audio features for tracks"""
        async with httpx.AsyncClient() as client:
            ids = ",".join(track_ids)
            response = await client.get(
                f"{self.BASE_URL}/audio-features",
                headers=self.headers,
                params={"ids": ids}
            )
            response.raise_for_status()
            return response.json()["audio_features"]

    async def get_recently_played(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently played tracks"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/me/player/recently-played",
                headers=self.headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()["items"]
