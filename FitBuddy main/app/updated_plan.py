"""
updated_plan.py
-----------------
Revises an existing workout plan based on free-text user feedback, using
Gemini's Pro-tier model via the current google-genai SDK.
"""

from app.gemini_config import client, GEMINI_PRO_MODEL, GOOGLE_API_KEY


def update_workout_plan(original_plan: str, feedback: str) -> str:
    """
    Sends the original 7-day plan plus the user's feedback to Gemini's
    Pro-tier model and returns a revised plan that incorporates the
    requested changes.
    """
    if not client or not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        return (
            "[Gemini API key not configured] Add a valid GOOGLE_API_KEY to "
            "your .env file to get a real AI-revised plan."
        )

    prompt = f"""
You are a certified personal fitness trainer. Below is a client's current
7-day workout plan, followed by feedback they submitted. Revise the plan to
incorporate their feedback while keeping the same "Day 1" through "Day 7"
structure, warm-up/cooldown notes, and overall formatting style.

--- ORIGINAL PLAN ---
{original_plan}

--- USER FEEDBACK ---
{feedback}

Return only the complete revised 7-day plan in plain text, with the same
day-by-day structure as the original.
"""

    try:
        response = client.models.generate_content(model=GEMINI_PRO_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as exc:  # pragma: no cover - network/SDK errors
        return f"[Error updating workout plan: {exc}]"
