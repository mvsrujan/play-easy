# Add this to any router file (like analysis.py or create a new debug.py)
from fastapi import APIRouter
import google.generativeai as genai
from app.config import settings

router = APIRouter()


@router.get("/debug/list-models")
async def list_gemini_models():
    """List all available Gemini models"""
    genai.configure(api_key=settings.gemini_api_key)

    models = []
    for m in genai.list_models():
        models.append({
            "name": m.name,
            "display_name": m.display_name,
            "description": m.description,
            "supported_methods": m.supported_generation_methods
        })

    return {"models": models}
