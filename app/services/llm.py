import google.generativeai as genai
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class LLMService(ABC):
    """Abstract base class for LLM services"""

    @abstractmethod
    async def analyze_songs(self, songs_data: List[Dict[str, Any]], instrument: str = "guitar") -> str:
        pass


class GeminiService(LLMService):
    """Gemini LLM implementation"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def analyze_songs(self, songs_data: List[Dict[str, Any]], instrument: str = "guitar") -> str:
        prompt = f"""Analyze these songs and identify which ones would be easiest to play on {instrument} for a beginner to intermediate player. Consider tempo, key, complexity, and style.

Songs with their audio features:
{songs_data}

For each song, rate it as "Easy", "Medium", or "Hard" and explain why in 1-2 sentences. Focus on technical difficulty specific to {instrument}. Format your response as a list."""

        response = self.model.generate_content(prompt)
        return response.text
