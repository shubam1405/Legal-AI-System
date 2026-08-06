"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any, Dict

from backend.api.dependencies import get_db_session, get_current_active_user
from backend.services.auth_service import AuthService
from backend.database.models import User
from pydantic import BaseModel, EmailStr

__all__ = ["router"]

router = APIRouter()

class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db_session)
) -> Any:
    """Register a new user."""
    user = AuthService.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = AuthService.create_user(
        db=db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role=user_in.role
    )
    return user

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = AuthService.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = AuthService.create_access_token(
        subject=str(user.id)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout() -> Any:
    """Logout the current user."""
    return {"msg": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user
