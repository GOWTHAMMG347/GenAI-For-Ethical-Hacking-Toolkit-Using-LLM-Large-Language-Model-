# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Look for the variable name, not the actual key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set. Please add it to your .env file.")
