"""
Case repository for managing legal cases.
"""
import uuid
from sqlalchemy.orm import Session

from backend.database.models import Case
from backend.utils.exceptions import DatabaseError

class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_case(self, created_by_user_id: uuid.UUID, title: str, case_type: str, **fields) -> Case:
        try:
            case = Case(
                created_by_user_id=created_by_user_id,
                title=title,
                case_type=case_type,
                **fields
            )
            self.db.add(case)
            self.db.commit()
            self.db.refresh(case)
            return case
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create case: {str(e)}")

    def get_by_id(self, case_id: uuid.UUID) -> Case | None:
        return self.db.query(Case).filter(Case.id == case_id).first()

    def list_by_lawyer(self, lawyer_id: uuid.UUID) -> list[Case]:
        return self.db.query(Case).filter(Case.lawyer_id == lawyer_id).order_by(Case.updated_at.desc()).all()

    def list_by_user(self, user_id: uuid.UUID) -> list[Case]:
        return self.db.query(Case).filter(Case.created_by_user_id == user_id).order_by(Case.updated_at.desc()).all()

    def update_case(self, case_id: uuid.UUID, updates: dict) -> Case | None:
        try:
            case = self.get_by_id(case_id)
            if not case:
                return None
            
            for key, value in updates.items():
                if hasattr(case, key):
                    setattr(case, key, value)
                    
            self.db.commit()
            self.db.refresh(case)
            return case
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update case: {str(e)}")

    def delete_case(self, case_id: uuid.UUID) -> bool:
        try:
            case = self.get_by_id(case_id)
            if not case:
                return False
            
            self.db.delete(case)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete case: {str(e)}")
