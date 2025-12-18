# test_models.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {api_key[:10]}..." if api_key else "API Key NOT found!")

# Configure genai
genai.configure(api_key=api_key)

# List models
print("\nAvailable models that support generateContent:")
print("-" * 60)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
