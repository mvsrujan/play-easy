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
        prompt = f"""Analyze these songs for {instrument} difficulty (beginner to intermediate level). Consider tempo, key, complexity, chord progressions, and playing techniques.

Songs with audio features:
{songs_data}

Format your response EXACTLY like this:

# Easy Songs

## Song Title - Artist
Brief explanation of why this is easy to play (1-2 sentences focusing on simple chords, slow tempo, basic strumming patterns, etc.)

## Another Easy Song - Artist
Explanation...

# Medium Songs

## Song Title - Artist
Brief explanation of why this is medium difficulty (1-2 sentences focusing on specific techniques, tempo changes, barre chords, etc.)

# Hard Songs

## Song Title - Artist
Brief explanation of why this is hard (1-2 sentences focusing on advanced techniques, complex rhythms, fast tempo, etc.)

IMPORTANT:
- Group ALL songs by difficulty: Easy first, then Medium, then Hard
- Use ## for each song title
- Keep explanations concise and specific to {instrument} playing techniques
- If a song doesn't fit any category well, put it in the closest match
- Every song must be categorized"""

        response = self.model.generate_content(prompt)
        return response.text
