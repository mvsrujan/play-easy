from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.models.session import session_manager
from app.services.spotify import SpotifyService
from app.services.llm import GeminiService
from app.config import settings
import markdown  # You'll need to: pip install markdown

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
        analysis_text = await llm.analyze_songs(songs_data, instrument)

        # Convert markdown to HTML
        analysis = markdown.markdown(analysis_text)

    except Exception as e:
        analysis = f"<p>Error analyzing songs: {str(e)}</p>"

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
                background: #191414;
                min-height: 100vh;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }}
            h1 {{ 
                color: #333; 
                margin-bottom: 30px;
                border-bottom: 3px solid #1DB954;
                padding-bottom: 15px;
            }}
            .analysis {{
                line-height: 1.8;
                color: #444;
            }}
            .analysis h1 {{
                color: #1DB954;
                font-size: 1.8em;
                margin-top: 30px;
                margin-bottom: 15px;
                border-bottom: 2px solid #1DB954;
                padding-bottom: 10px;
            }}
            .analysis h2 {{
                color: #555;
                font-size: 1.3em;
                margin-top: 20px;
                margin-bottom: 10px;
                padding-left: 10px;
                border-left: 4px solid #1DB954;
            }}
            .analysis p {{
                margin: 10px 0;
                padding-left: 15px;
            }}
            .analysis ul {{
                margin: 10px 0;
                padding-left: 30px;
            }}
            .analysis li {{
                margin: 8px 0;
            }}
            .back-btn {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #1DB954;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .back-btn:hover {{ background: #1ed760; }}
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
