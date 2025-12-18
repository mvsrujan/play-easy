from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import secrets
from app.config import settings
from app.services.auth import SpotifyAuthService
from app.models.session import session_manager

router = APIRouter(tags=["auth"])


@router.get("/login")
async def login():
    """Initiate Spotify OAuth flow"""
    state = secrets.token_urlsafe(16)
    scope = "user-top-read user-read-recently-played"

    params = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": settings.spotify_redirect_uri,
        "state": state,
        "scope": scope
    }

    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(code: str, state: str):
    """Handle Spotify OAuth callback"""
    try:
        access_token = await SpotifyAuthService.exchange_code_for_token(code)
        session_id = secrets.token_urlsafe(16)
        session_manager.create_session(session_id, access_token)

        return RedirectResponse(url=f"/analyze?session_id={session_id}")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Authentication failed: {str(e)}")
