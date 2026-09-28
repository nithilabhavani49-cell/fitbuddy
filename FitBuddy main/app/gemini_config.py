"""
gemini_config.py
-----------------
Loads the Gemini API key from the environment (.env) and creates a single
shared google-genai Client that every other module imports and reuses.

Note: Google's older "google-generativeai" package (import google.generativeai
as genai / genai.configure(...) / genai.GenerativeModel(...)) reached end of
life on Nov 30, 2025. This project uses the current, actively maintained
"google-genai" SDK instead (from google import genai / genai.Client(...) /
client.models.generate_content(...)).
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads variables from a .env file in the project root, if present

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model names are overridable via .env in case Google renames/retires a model.
# gemini-2.5-pro / gemini-2.5-flash are the current stable models as of
# September 2026. If either one is retired later, set GEMINI_PRO_MODEL /
# GEMINI_FLASH_MODEL in your .env to a current model name from
# https://ai.google.dev/gemini-api/docs/models (e.g. gemini-3-flash-preview).
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")

client = None

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
    print(
        "\n[FitBuddy WARNING] GOOGLE_API_KEY is not set. "
        "Create a .env file (see .env.example) with a valid Gemini API key "
        "from https://aistudio.google.com/app/apikey before generating plans.\n"
    )
else:
    client = genai.Client(api_key=GOOGLE_API_KEY)
