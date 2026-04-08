from typing import List, Dict
from pydantic import BaseModel, Field, EmailStr

class PantryItem(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1)

class GeneratePlanRequest(BaseModel):
    budget_rub: float = Field(..., gt=0)
    days: int = Field(..., ge=1, le=7)
    meal_mode: str = Field(..., min_length=1)
    excluded_tags: List[str] = Field(default_factory=list)
    pantry_items: List[PantryItem] = Field(default_factory=list)
    price_overrides: Dict[str, float] = Field(default_factory=dict)
    user_note: str = ""

class ToggleFavoriteRequest(BaseModel):
    is_favorite: bool

class ReplaceBatchRequest(BaseModel):
    batch_number: int = Field(..., ge=1)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class UserResponse(BaseModel):
    id: int
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
