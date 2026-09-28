# FitBuddy — AI Fitness Plan Generator (Gemini + FastAPI)

FitBuddy generates a personalized 7-day workout plan and a matching
nutrition/recovery tip from a user's age, weight, fitness goal, and workout
intensity, using Google's Gemini models. Users can submit feedback to
regenerate an updated plan, and an admin dashboard lists every user and
their plans.

## Project structure

```
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── routes.py                 # All HTTP routes
│   ├── database.py               # SQLAlchemy models + CRUD helpers
│   ├── schemas.py                # Pydantic request models
│   ├── gemini_config.py          # Loads .env and configures the Gemini SDK
│   ├── gemini_generator.py       # generate_workout_gemini() — Gemini 1.5 Pro
│   ├── gemini_flash_generator.py # generate_nutrition_tip_with_flash() — Gemini Flash
│   └── updated_plan.py           # update_workout_plan() — Gemini 1.5 Pro
├── templates/
│   ├── index.html                # Input form
│   ├── result.html                # Plan, tip, feedback form
│   └── all_users.html            # Admin dashboard
├── static/
│   ├── css/style.css
│   └── images/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 1. Prerequisites

- Python 3.10+ installed
- A free Gemini API key from https://aistudio.google.com/app/apikey
- VS Code with the **Python** extension (recommended)

## 2. VS Code setup

1. Open the `FitBuddy` folder in VS Code: `File → Open Folder…`
2. Open a terminal in VS Code: `` Ctrl+` `` (or `View → Terminal`)
3. When VS Code detects `app/main.py`, make sure the correct Python
   interpreter is selected (bottom-right corner, or `Ctrl+Shift+P` →
   "Python: Select Interpreter") — pick the virtual environment you create
   in the next step once it exists.

## 3. Installation

Run these commands in the VS Code terminal, from the `FitBuddy` folder:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 4. Configure your Gemini API key

1. Copy `.env.example` to a new file named `.env` in the project root.
2. Open `.env` and paste your real key:

```
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

Without a valid key, the app still runs and the UI still works end-to-end,
but the workout plan / nutrition tip / feedback update text will show a
placeholder message instead of real AI output.

## 5. Run the application

From the `FitBuddy` folder, with the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

You should see output ending with something like:

```
Uvicorn running on http://127.0.0.1:8000
```

- App UI: http://127.0.0.1:8000
- Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs
- Admin dashboard: http://127.0.0.1:8000/view-all-users

The SQLite database file `fitbuddy.db` is created automatically in the
project root the first time you run the app.

## 6. Testing the app

### A. Manual walkthrough (recommended first test)

1. Go to http://127.0.0.1:8000
2. Fill in the form: Name, a unique User ID, Age, Weight, Fitness Goal,
   Workout Intensity → click **Generate Plan**.
3. You should land on the results page with a 7-day workout plan and a
   nutrition tip.
4. In the feedback box at the bottom, enter the same User ID and some
   feedback (e.g. "add more cardio, include a yoga day") → click
   **Update My Plan**.
5. You should see both the original plan and the newly updated plan.
6. Go to http://127.0.0.1:8000/view-all-users to confirm the user and both
   plan versions appear in the admin table. Try the **Delete** button on a
   test user to confirm removal works.

### B. Testing via the interactive API docs

1. Open http://127.0.0.1:8000/docs
2. Expand `POST /generate-workout`, click **Try it out**, fill in the form
   fields, and execute — you'll get the rendered HTML result back.
3. Expand `POST /submit-feedback` and repeat with the same `user_id` plus a
   `feedback` string.

### C. Quick command-line smoke test

With the server running in one terminal, run this in a second terminal:

```bash
curl -X POST http://127.0.0.1:8000/generate-workout \
  -F "user_id=test01" \
  -F "username=Test User" \
  -F "age=25" \
  -F "weight=70" \
  -F "goal=muscle gain" \
  -F "intensity=medium"
```

You should get back the HTML of the results page. If it contains a 7-day
plan (or the placeholder message when no API key is set), the backend,
database, and template rendering are all working correctly.

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` for fastapi/uvicorn/etc. | Make sure the virtual environment is activated and `pip install -r requirements.txt` finished without errors. |
| Plans show `[Gemini API key not configured]` | Double-check `.env` exists (not just `.env.example`) and `GOOGLE_API_KEY` is set to a real key, then restart the server. |
| `[Error generating workout plan: ...]` | Usually means the API key is invalid/expired, you're offline, or you've hit a rate limit — check the exact error text for details. |
| Port 8000 already in use | Run `uvicorn app.main:app --reload --port 8001` and visit that port instead. |
| Templates not found | Confirm you're running `uvicorn` from the project root (`FitBuddy/`), not from inside `app/`. |

## 8. How the AI integration works

- **`generate_workout_gemini()`** (`gemini_generator.py`) — sends the
  user's profile to **Gemini 1.5 Pro** to produce a structured, day-by-day
  7-day workout plan (warm-up, main workout, cooldown).
- **`generate_nutrition_tip_with_flash()`** (`gemini_flash_generator.py`) —
  sends the user's goal to the lightweight **Gemini Flash** model for a
  fast, practical nutrition/recovery tip.
- **`update_workout_plan()`** (`updated_plan.py`) — sends the original plan
  plus the user's feedback back to **Gemini 1.5 Pro**, which returns a
  revised plan; both versions are kept in the database.

Enjoy building on FitBuddy!
