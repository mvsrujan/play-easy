import httpx
from app.config import settings


class SpotifyAuthService:
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    @staticmethod
    async def exchange_code_for_token(code: str) -> str:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SpotifyAuthService.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.spotify_redirect_uri,
                    "client_id": settings.spotify_client_id,
                    "client_secret": settings.spotify_client_secret
                }
            )
            response.raise_for_status()
            return response.json()["access_token"]
