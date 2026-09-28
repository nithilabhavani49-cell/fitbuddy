"""
schemas.py
----------
Pydantic models used to validate incoming form data / request bodies.
"""

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    user_id: str = Field(..., description="Unique ID chosen by the user")
    username: str = Field(..., description="Display name of the user")
    age: int = Field(..., gt=0, lt=120)
    weight: float = Field(..., gt=0)
    goal: str = Field(..., description="e.g. weight loss, muscle gain, general wellness")
    intensity: str = Field(..., description="low, medium, or high")


class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str
