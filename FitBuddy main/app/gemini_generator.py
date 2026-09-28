"""
gemini_generator.py
--------------------
Generates a personalized 7-day workout plan using Gemini's Pro-tier model,
via the current google-genai SDK.
"""

from app.gemini_config import client, GEMINI_PRO_MODEL, GOOGLE_API_KEY


def _build_prompt(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    return f"""
You are a certified personal fitness trainer. Create a detailed, structured
7-day workout plan for the following client.

Client details:
- Name: {username}
- Age: {age}
- Weight: {weight} kg
- Fitness goal: {goal}
- Preferred workout intensity: {intensity}

Formatting rules:
- Organize the plan strictly by "Day 1" through "Day 7".
- For each day include: a short focus title (e.g. "Full Body", "Cardio",
  "Rest & Recovery"), a brief warm-up (5-10 minutes), the main workout with
  exercise names, sets, reps or duration, and rest intervals, and a short
  cooldown / recovery note.
- Include at least one rest or active-recovery day.
- Keep the tone motivating and the instructions easy to follow for someone
  at a {intensity} intensity level.
- Use plain text with clear line breaks between days - do not use markdown
  tables.
"""


def generate_workout_gemini(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    """
    Calls Gemini's Pro-tier model to generate a structured 7-day workout plan.
    Returns the plan as plain text, ready to be displayed inside a <pre> block.
    """
    if not client or not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        return (
            "[Gemini API key not configured]\n"
            "Add a valid GOOGLE_API_KEY to your .env file to generate a real "
            "AI-powered workout plan. This is placeholder text so the app can "
            "still be demoed end-to-end."
        )

    try:
        prompt = _build_prompt(username, age, weight, goal, intensity)
        response = client.models.generate_content(model=GEMINI_PRO_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as exc:  # pragma: no cover - network/SDK errors
        return f"[Error generating workout plan: {exc}]"
