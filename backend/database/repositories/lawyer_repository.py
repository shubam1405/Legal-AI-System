"""
Lawyer repository for managing lawyer profiles.
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text, or_

from backend.database.models import Lawyer
from backend.utils.exceptions import DatabaseError

class LawyerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_profile(self, user_id: uuid.UUID, **fields) -> Lawyer:
        try:
            lawyer = Lawyer(user_id=user_id, **fields)
            self.db.add(lawyer)
            self.db.commit()
            self.db.refresh(lawyer)
            return lawyer
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create lawyer profile: {str(e)}")

    def get_by_user_id(self, user_id: uuid.UUID) -> Lawyer | None:
        return self.db.query(Lawyer).filter(Lawyer.user_id == user_id).first()

    def get_by_id(self, lawyer_id: uuid.UUID) -> Lawyer | None:
        return self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

    def get_all(self) -> list[Lawyer]:
        return self.db.query(Lawyer).all()

    def search_by_specializations(self, specializations: list[str]) -> list[Lawyer]:
        """Search lawyers matching ANY of the given specializations."""
        if not specializations:
            return self.get_all()
        
        # Cast JSON to String for LIKE matching to prevent PostgreSQL json ~~ text errors
        from sqlalchemy import cast, String
        conditions = [cast(Lawyer.specializations, String).like(f'%"{spec}"%') for spec in specializations]
        query = self.db.query(Lawyer).filter(or_(*conditions)).order_by(Lawyer.success_rate.desc())
        return query.all()

    def update_profile(self, lawyer_id: uuid.UUID, updates: dict) -> Lawyer | None:
        try:
            lawyer = self.get_by_id(lawyer_id)
            if not lawyer:
                return None
            
            for key, value in updates.items():
                if hasattr(lawyer, key):
                    setattr(lawyer, key, value)
                    
            self.db.commit()
            self.db.refresh(lawyer)
            return lawyer
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update lawyer profile: {str(e)}")
