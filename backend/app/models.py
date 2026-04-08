from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="main")
    difficulty = Column(String(50), nullable=False)
    estimated_cost_rub = Column(Float, nullable=False)
    cooking_time_min = Column(Integer, nullable=False)
    portions = Column(Integer, nullable=False, default=4)
    protein_type = Column(String(50), nullable=False, default="mixed")
    is_batch_friendly = Column(Boolean, nullable=False, default=True)
    is_vegetarian = Column(Boolean, nullable=False, default=False)
    is_vegan = Column(Boolean, nullable=False, default=False)
    tags = Column(Text, nullable=False, default="")
    ingredients_json = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    budget_rub = Column(Float, nullable=False)
    days = Column(Integer, nullable=False)
    meals_per_day = Column(Integer, nullable=False, default=1)
    excluded_tags = Column(Text, nullable=False, default="")
    pantry_items_json = Column(Text, nullable=False, default="[]")
    total_cost_rub = Column(Float, nullable=False)
    llm_reasoning = Column(Text, nullable=False, default="")
    plan_json = Column(Text, nullable=False, default="{}")
    is_favorite = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="meal_plans")
