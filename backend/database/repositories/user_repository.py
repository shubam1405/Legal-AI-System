"""
User repository for managing users and session tokens.
"""
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database.models import User, SessionToken
from backend.utils.exceptions import DatabaseError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, password: str, name: str, role: str = 'public') -> User:
        try:
            hashed_password = pwd_context.hash(password)
            user = User(
                email=email,
                hashed_password=hashed_password,
                name=name,
                role=role
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise DatabaseError("User with this email already exists.")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create user: {str(e)}")

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def update_user(self, user_id: uuid.UUID, updates: dict) -> User | None:
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update user: {str(e)}")

    def create_session(self, user_id: uuid.UUID) -> SessionToken:
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            
            session_token = SessionToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )
            self.db.add(session_token)
            self.db.commit()
            self.db.refresh(session_token)
            return session_token
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create session: {str(e)}")

    def validate_session(self, token: str) -> User | None:
        session_token = self.db.query(SessionToken).filter(SessionToken.token == token).first()
        if not session_token or session_token.is_expired:
            return None
        return session_token.user

    def delete_session(self, token: str) -> None:
        try:
            session_token = self.db.query(SessionToken).filter(SessionToken.token == token).first()
            if session_token:
                self.db.delete(session_token)
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete session: {str(e)}")
