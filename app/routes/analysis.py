from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.models.session import session_manager
from app.services.spotify import SpotifyService
from app.services.llm import GeminiService
from app.config import settings

router = APIRouter(tags=["analysis"])


@router.get("/analyze", response_class=HTMLResponse)
async def analyze(
    session_id: str,
    instrument: str = Query(
        default="guitar", description="Instrument to analyze for")
):
    """Analyze user's songs for instrument difficulty"""
    access_token = session_manager.get_session(session_id)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid session")

    # Initialize services
    spotify = SpotifyService(access_token)
    llm = GeminiService(settings.gemini_api_key)

    try:
        # Fetch tracks (now includes embedded audio features)
        tracks = await spotify.get_top_tracks(limit=20)

        # Prepare data using embedded audio features
        songs_data = []
        for track in tracks:
            feat = track.get('audio_features', {})
            if feat:
                songs_data.append({
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "tempo": feat.get("tempo", 120),
                    "key": feat.get("key", 0),
                    "mode": feat.get("mode", 1),
                    "time_signature": feat.get("time_signature", 4),
                    "acousticness": feat.get("acousticness", 0.3),
                    "energy": feat.get("energy", 0.5)
                })

        # Analyze with LLM
        analysis = await llm.analyze_songs(songs_data, instrument)

    except Exception as e:
        analysis = f"Error analyzing songs: {str(e)}"

    # Render results
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your {instrument.title()}-Friendly Songs</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 900px;
                margin: 30px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }}
            h1 {{ color: #333; margin-bottom: 30px; }}
            .analysis {{
                white-space: pre-wrap;
                line-height: 1.8;
                color: #444;
            }}
            .back-btn {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .back-btn:hover {{ background: #5568d3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎸 Your {instrument.title()}-Friendly Songs</h1>
            <div class="analysis">{analysis}</div>
            <a href="/" class="back-btn">← Start Over</a>
        </div>
    </body>
    </html>
    """

    return html
