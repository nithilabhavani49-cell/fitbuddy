"""
routes.py
---------
Defines every HTTP route for FitBuddy. Bridges the frontend templates, the
Gemini AI generation modules, and the SQLite database.

Routes:
    GET  /                -> index.html (user input form)
    POST /generate-workout -> generates plan + tip, saves to DB, shows result.html
    POST /submit-feedback  -> revises plan with feedback, shows result.html
    GET  /view-all-users   -> admin dashboard (all_users.html)
    POST /delete-user      -> removes a user + their plan (used by admin view)
"""

import os

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import (
    get_db,
    save_user,
    save_plan,
    update_plan,
    get_original_plan,
    get_user,
    get_plan,
    get_all_users,
    get_all_plans,
    delete_user,
)
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# ---------------------------------------------------------------------------
# Home route - the input form
# ---------------------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


# ---------------------------------------------------------------------------
# Generate a brand-new 7-day workout plan + nutrition tip
# ---------------------------------------------------------------------------
@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    user_id: str = Form(...),
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1. Persist the user's profile info
    save_user(db, user_id=user_id, username=username, age=age, weight=weight, goal=goal, intensity=intensity)

    # 2. Call Gemini 1.5 Pro for the structured 7-day plan
    workout_plan = generate_workout_gemini(username, age, weight, goal, intensity)

    # 3. Call Gemini Flash for a quick nutrition/recovery tip
    nutrition_tip = generate_nutrition_tip_with_flash(goal)

    # 4. Save the plan + tip
    save_plan(db, user_id=user_id, original_plan=workout_plan, nutrition_tip=nutrition_tip)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "user_id": user_id,
            "username": username,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated_plan": None,
            "message": None,
        },
    )


# ---------------------------------------------------------------------------
# Revise an existing plan based on user feedback
# ---------------------------------------------------------------------------
@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)
    original_plan = get_original_plan(db, user_id)

    if not user or not original_plan:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "user_id": user_id,
                "username": None,
                "age": None,
                "weight": None,
                "goal": None,
                "intensity": None,
                "workout_plan": None,
                "nutrition_tip": None,
                "updated_plan": None,
                "message": "No existing plan found for this User ID. Please generate a plan first.",
            },
        )

    # Ask Gemini Pro to revise the plan using the feedback
    revised_plan = update_workout_plan(original_plan, feedback)

    # Refresh the nutrition tip too, in case the goal-related advice should change
    nutrition_tip = generate_nutrition_tip_with_flash(user.goal)

    update_plan(db, user_id=user_id, updated_plan=revised_plan, feedback=feedback, nutrition_tip=nutrition_tip)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": original_plan,
            "nutrition_tip": nutrition_tip,
            "updated_plan": revised_plan,
            "message": "Your plan has been updated based on your feedback!",
        },
    )


# ---------------------------------------------------------------------------
# Admin dashboard - view every registered user + their plans
# ---------------------------------------------------------------------------
@router.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    plans = {plan.user_id: plan for plan in get_all_plans(db)}

    rows = []
    for user in users:
        plan = plans.get(user.user_id)
        rows.append(
            {
                "user": user,
                "original_plan": plan.original_plan if plan else None,
                "updated_plan": plan.updated_plan if plan else None,
                "nutrition_tip": plan.nutrition_tip if plan else None,
            }
        )

    return templates.TemplateResponse("all_users.html", {"request": request, "rows": rows})


# ---------------------------------------------------------------------------
# Admin action - delete a user and their plan
# ---------------------------------------------------------------------------
@router.post("/delete-user")
async def delete_user_route(user_id: str = Form(...), db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)
