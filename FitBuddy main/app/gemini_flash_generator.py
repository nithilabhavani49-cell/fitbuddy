"""
gemini_flash_generator.py
--------------------------
Generates a short, practical nutrition/recovery tip using Gemini's
lightweight Flash-tier model, via the current google-genai SDK.
"""

from app.gemini_config import client, GEMINI_FLASH_MODEL, GOOGLE_API_KEY


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Calls Gemini's Flash-tier model to generate a concise nutrition or
    recovery tip relevant to the user's fitness goal (e.g. weight loss,
    muscle gain).
    """
    if not client or not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        return (
            "[Gemini API key not configured] Add a valid GOOGLE_API_KEY to "
            "your .env file to get a real AI-generated tip."
        )

    prompt = (
        f"Give one short, practical nutrition or recovery tip (2-3 sentences max) "
        f"for someone whose fitness goal is '{goal}'. Be specific and actionable "
        f"(mention a food, habit, or recovery practice). Do not use markdown."
    )

    try:
        response = client.models.generate_content(model=GEMINI_FLASH_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as exc:  # pragma: no cover - network/SDK errors
        return f"[Error generating nutrition tip: {exc}]"
