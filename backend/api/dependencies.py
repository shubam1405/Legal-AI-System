"""
Dependencies for the FastAPI application.
"""
from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import User
from backend.services.auth_service import AuthService

__all__ = ["get_current_user", "get_current_active_user", "get_db_session"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_db_session() -> Generator[Session, None, None]:
    """Yields a database session."""
    yield from get_db()

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db_session)]
) -> User:
    """Retrieves the current user from the token."""
    user = AuthService.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Retrieves the current active user."""
    return current_user
