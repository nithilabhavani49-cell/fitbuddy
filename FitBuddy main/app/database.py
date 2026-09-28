"""
database.py
------------
Handles the SQLite database connection, SQLAlchemy ORM models, and all
CRUD (create / read / update) helper functions used by routes.py.

Tables:
    users -> one row per registered user (identified by their own user_id)
    plans -> one row per user, storing the original AI-generated workout
             plan, the (optional) feedback-updated plan, and the nutrition
             tip that goes with the plan.
"""

import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "fitbuddy.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), unique=True, nullable=False)
    original_plan = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="plan")


def init_db():
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# CRUD helper functions (used directly by routes.py)
# ---------------------------------------------------------------------------
def save_user(db, user_id: str, username: str, age: int, weight: float, goal: str, intensity: str) -> User:
    """Create a new user, or return the existing one if the user_id already exists."""
    existing = db.query(User).filter(User.user_id == user_id).first()
    if existing:
        # Update basic info in case the user re-submits the form with new details
        existing.username = username
        existing.age = age
        existing.weight = weight
        existing.goal = goal
        existing.intensity = intensity
        db.commit()
        db.refresh(existing)
        return existing

    user = User(
        user_id=user_id,
        username=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_plan(db, user_id: str, original_plan: str, nutrition_tip: str) -> Plan:
    """Create (or overwrite) the plan row tied to a given user_id."""
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if plan:
        plan.original_plan = original_plan
        plan.nutrition_tip = nutrition_tip
        plan.updated_plan = None
        plan.feedback = None
    else:
        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db, user_id: str, updated_plan: str, feedback: str, nutrition_tip: str = None) -> Plan:
    """Store a feedback-revised plan alongside the original plan."""
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if not plan:
        raise ValueError(f"No existing plan found for user_id={user_id}")

    plan.updated_plan = updated_plan
    plan.feedback = feedback
    if nutrition_tip:
        plan.nutrition_tip = nutrition_tip
    db.commit()
    db.refresh(plan)
    return plan


def get_original_plan(db, user_id: str) -> str:
    """Return the most recent plan text (updated if it exists, else original)."""
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if not plan:
        return None
    return plan.original_plan


def get_user(db, user_id: str) -> User:
    return db.query(User).filter(User.user_id == user_id).first()


def get_plan(db, user_id: str) -> Plan:
    return db.query(Plan).filter(Plan.user_id == user_id).first()


def get_all_users(db):
    return db.query(User).all()


def get_all_plans(db):
    return db.query(Plan).all()


def delete_user(db, user_id: str) -> bool:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return False
    db.delete(user)  # cascade also removes the linked Plan row
    db.commit()
    return True
