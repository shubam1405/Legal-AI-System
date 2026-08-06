"""
Document repository for managing document metadata.
"""
import uuid
from sqlalchemy.orm import Session

from backend.database.models import Document
from backend.utils.exceptions import DatabaseError

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, uploaded_by_user_id: uuid.UUID, file_name: str, file_path: str, collection_name: str, case_id: uuid.UUID = None, **fields) -> Document:
        try:
            doc = Document(
                uploaded_by_user_id=uploaded_by_user_id,
                file_name=file_name,
                file_path=file_path,
                collection_name=collection_name,
                case_id=case_id,
                **fields
            )
            self.db.add(doc)
            self.db.commit()
            self.db.refresh(doc)
            return doc
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create document: {str(e)}")

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_by_case(self, case_id: uuid.UUID) -> list[Document]:
        return self.db.query(Document).filter(Document.case_id == case_id).all()

    def list_by_user(self, user_id: uuid.UUID) -> list[Document]:
        return self.db.query(Document).filter(Document.uploaded_by_user_id == user_id).all()

    def delete_document(self, document_id: uuid.UUID) -> bool:
        try:
            doc = self.get_by_id(document_id)
            if not doc:
                return False
            
            self.db.delete(doc)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete document: {str(e)}")
