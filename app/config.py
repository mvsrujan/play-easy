import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    spotify_client_id: str
    spotify_client_secret: str
    # redirect_uri: str = "http://127.0.0.1:8000/callback"
    spotify_redirect_uri: str
    gemini_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()
