from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes import auth, analysis
from app.config import settings
import os

app = FastAPI(title="Guitar Song Analyzer")

# Include routers
app.include_router(auth.router)
app.include_router(analysis.router)


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Guitar Song Analyzer</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }
            h1 { color: #333; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            .login-btn {
                background: #1DB954;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                font-weight: bold;
            }
            .login-btn:hover { background: #1ed760; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎸 Guitar Song Analyzer</h1>
            <p class="subtitle">Discover which songs from your Spotify are easy to play on guitar!</p>
            <a href="/login" class="login-btn">Login with Spotify</a>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
