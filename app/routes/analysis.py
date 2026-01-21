from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.models.session import session_manager
from app.services.spotify import SpotifyService
from app.services.llm import GeminiService
from app.config import settings
import markdown

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
        # Fetch 50 tracks (now includes embedded audio features)
        tracks = await spotify.get_top_tracks(limit=50)

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
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                background: #191414;
                min-height: 100vh;
                padding: 40px 20px;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
                padding: 50px 40px;
                border-radius: 16px;
                margin-bottom: 40px;
                box-shadow: 0 8px 32px rgba(29, 185, 84, 0.3);
            }}
            
            h1 {{
                color: white;
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 1.1em;
            }}
            
            .difficulty-section {{
                background: white;
                margin-bottom: 20px;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .difficulty-section:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            }}
            
            .difficulty-header {{
                padding: 24px 28px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background 0.2s;
                position: relative;
            }}
            
            .difficulty-header::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 5px;
            }}
            
            .difficulty-header.easy::before {{
                background: linear-gradient(180deg, #1DB954 0%, #1ed760 100%);
            }}
            
            .difficulty-header.medium::before {{
                background: linear-gradient(180deg, #FFA500 0%, #FFB733 100%);
            }}
            
            .difficulty-header.hard::before {{
                background: linear-gradient(180deg, #FF4444 0%, #FF6666 100%);
            }}
            
            .difficulty-header:hover {{
                background: #fafafa;
            }}
            
            .difficulty-header-content {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .difficulty-title {{
                font-size: 1.4em;
                font-weight: 600;
                letter-spacing: -0.02em;
            }}
            
            .difficulty-title.easy {{
                color: #1DB954;
            }}
            
            .difficulty-title.medium {{
                color: #FFA500;
            }}
            
            .difficulty-title.hard {{
                color: #FF4444;
            }}
            
            .song-count {{
                background: #f0f0f0;
                color: #666;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 500;
                margin-left: 12px;
            }}
            
            .arrow {{
                font-size: 1em;
                color: #999;
                transition: transform 0.3s ease;
            }}
            
            .arrow.open {{
                transform: rotate(180deg);
            }}
            
            .difficulty-content {{
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            
            .difficulty-content.open {{
                max-height: 10000px;
            }}
            
            .songs-container {{
                padding: 20px 28px 28px 28px;
            }}
            
            .song-item {{
                padding: 20px;
                margin-bottom: 12px;
                background: #fafafa;
                border-radius: 10px;
                border-left: 4px solid;
                transition: all 0.2s;
            }}
            
            .song-item.easy {{
                border-left-color: #1DB954;
            }}
            
            .song-item.medium {{
                border-left-color: #FFA500;
            }}
            
            .song-item.hard {{
                border-left-color: #FF4444;
            }}
            
            .song-item:hover {{
                background: #f5f5f5;
                transform: translateX(4px);
            }}
            
            .song-item:last-child {{
                margin-bottom: 0;
            }}
            
            .song-title {{
                font-size: 1.15em;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 8px;
                line-height: 1.3;
            }}
            
            .song-description {{
                color: #666;
                line-height: 1.6;
                font-size: 0.95em;
            }}
            
            .empty-state {{
                text-align: center;
                padding: 40px 20px;
                color: #999;
                font-style: italic;
            }}
            
            .back-btn {{
                display: inline-block;
                margin-top: 30px;
                padding: 14px 28px;
                background: white;
                color: #1DB954;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
                transition: all 0.2s;
                border: 2px solid #1DB954;
            }}
            
            .back-btn:hover {{
                background: #1DB954;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
            }}
            
            @media (max-width: 768px) {{
                .header {{
                    padding: 30px 24px;
                }}
                
                h1 {{
                    font-size: 2em;
                }}
                
                .difficulty-title {{
                    font-size: 1.2em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎸 Your {instrument.title()}-Friendly Songs</h1>
                <p class="subtitle">Analyzing your top 100 tracks from Spotify</p>
            </div>
            
            <div class="difficulty-section">
                <div class="difficulty-header easy" onclick="toggleSection('easy')">
                    <div class="difficulty-header-content">
                        <div>
                            <span class="difficulty-title easy">Easy Songs</span>
                            <span class="song-count" id="easy-count">0</span>
                        </div>
                    </div>
                    <span class="arrow" id="arrow-easy">▼</span>
                </div>
                <div class="difficulty-content" id="content-easy">
                    <div class="songs-container" id="easy-songs"></div>
                </div>
            </div>

            <div class="difficulty-section">
                <div class="difficulty-header medium" onclick="toggleSection('medium')">
                    <div class="difficulty-header-content">
                        <div>
                            <span class="difficulty-title medium">Medium Songs</span>
                            <span class="song-count" id="medium-count">0</span>
                        </div>
                    </div>
                    <span class="arrow" id="arrow-medium">▼</span>
                </div>
                <div class="difficulty-content" id="content-medium">
                    <div class="songs-container" id="medium-songs"></div>
                </div>
            </div>

            <div class="difficulty-section">
                <div class="difficulty-header hard" onclick="toggleSection('hard')">
                    <div class="difficulty-header-content">
                        <div>
                            <span class="difficulty-title hard">Hard Songs</span>
                            <span class="song-count" id="hard-count">0</span>
                        </div>
                    </div>
                    <span class="arrow" id="arrow-hard">▼</span>
                </div>
                <div class="difficulty-content" id="content-hard">
                    <div class="songs-container" id="hard-songs"></div>
                </div>
            </div>

            <a href="/" class="back-btn">← Start Over</a>
        </div>

        <script>
            // Parse the analysis and organize by difficulty
            const analysisHTML = `{analysis}`;
            const parser = new DOMParser();
            const doc = parser.parseFromString(analysisHTML, 'text/html');
            
            const sections = {{'easy': [], 'medium': [], 'hard': []}};
            let currentDifficulty = null;
            
            // Parse the markdown-converted HTML
            doc.body.childNodes.forEach(node => {{
                if (node.tagName === 'H1') {{
                    const text = node.textContent.toLowerCase();
                    if (text.includes('easy')) currentDifficulty = 'easy';
                    else if (text.includes('medium')) currentDifficulty = 'medium';
                    else if (text.includes('hard')) currentDifficulty = 'hard';
                }} else if (node.tagName === 'H2' && currentDifficulty) {{
                    const songTitle = node.textContent;
                    let description = '';
                    let nextNode = node.nextSibling;
                    while (nextNode && nextNode.tagName !== 'H2' && nextNode.tagName !== 'H1') {{
                        if (nextNode.textContent) {{
                            description += nextNode.textContent;
                        }}
                        nextNode = nextNode.nextSibling;
                    }}
                    sections[currentDifficulty].push({{
                        title: songTitle,
                        description: description.trim()
                    }});
                }}
            }});
            
            // Populate each section
            ['easy', 'medium', 'hard'].forEach(difficulty => {{
                const container = document.getElementById(`${{difficulty}}-songs`);
                const countBadge = document.getElementById(`${{difficulty}}-count`);
                
                if (sections[difficulty].length === 0) {{
                    container.innerHTML = '<div class="empty-state">No songs in this category</div>';
                    countBadge.textContent = '0';
                }} else {{
                    countBadge.textContent = sections[difficulty].length;
                    sections[difficulty].forEach(song => {{
                        const songDiv = document.createElement('div');
                        songDiv.className = `song-item ${{difficulty}}`;
                        songDiv.innerHTML = `
                            <div class="song-title">${{song.title}}</div>
                            <div class="song-description">${{song.description}}</div>
                        `;
                        container.appendChild(songDiv);
                    }});
                }}
            }});
            
            function toggleSection(difficulty) {{
                const content = document.getElementById(`content-${{difficulty}}`);
                const arrow = document.getElementById(`arrow-${{difficulty}}`);
                content.classList.toggle('open');
                arrow.classList.toggle('open');
            }}
        </script>
    </body>
    </html>
    """

    return html
