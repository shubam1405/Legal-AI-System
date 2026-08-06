"""
Authentication service.
"""

from typing import Optional
from sqlalchemy.orm import Session
from backend.database.repositories.user_repository import UserRepository

__all__ = ["AuthService"]


class AuthService:
    """Service for handling user authentication and registration."""

    def __init__(self, db: Session):
        """
        Initialize the AuthService.
        
        Args:
            db (Session): Database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)

    def login(self, email: str, password: str) -> Optional[dict]:
        """
        Authenticate a user by email and password.
        
        Args:
            email (str): User email.
            password (str): User password.
            
        Returns:
            Optional[dict]: User data if successful, None otherwise.
        """
        user = self.user_repo.get_by_email(email)
        # Assuming verify_password exists on the user model or repository
        if user and hasattr(user, "verify_password") and user.verify_password(password):
            return user
        return None

    def register(self, email: str, password: str, **kwargs) -> dict:
        """
        Register a new user.
        
        Args:
            email (str): User email.
            password (str): User password.
            **kwargs: Additional user attributes.
            
        Returns:
            dict: The newly created user.
        """
        return self.user_repo.create(email=email, password=password, **kwargs)

    def logout(self, token: str) -> bool:
        """
        Logout a user by invalidating their token.
        
        Args:
            token (str): The authentication token.
            
        Returns:
            bool: True if successful.
        """
        # Token invalidation logic here
        return True

    def get_current_user(self, token: str) -> Optional[dict]:
        """
        Retrieve the current user from a token.
        
        Args:
            token (str): The authentication token.
            
        Returns:
            Optional[dict]: User data if token is valid, None otherwise.
        """
        # Token decoding logic here
        return None
