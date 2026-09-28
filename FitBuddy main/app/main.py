"""
main.py
-------
FastAPI application entry point for FitBuddy.

Run with:
    uvicorn app.main:app --reload

Then visit:
    http://127.0.0.1:8000       -> the app
    http://127.0.0.1:8000/docs  -> interactive API docs
"""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Generates personalized 7-day workout plans and nutrition tips using Google Gemini models.",
    version="1.0.0",
)

# Serve static assets (CSS, images) at /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Register all application routes
app.include_router(router)


@app.on_event("startup")
def on_startup():
    """Create the SQLite database tables (if they don't already exist)."""
    init_db()
