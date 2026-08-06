"""
Document processing service.
"""

import os
import uuid
from sqlalchemy.orm import Session
from backend.database.repositories.document_repository import DocumentRepository
from backend.rag.loader import process_pdf
from backend.rag.vector_store import add_documents_to_store

__all__ = ["DocumentService"]


class DocumentService:
    """Service for processing and storing documents."""

    def __init__(self, db: Session):
        """
        Initialize the DocumentService.
        
        Args:
            db (Session): Database session.
        """
        self.db = db
        self.document_repo = DocumentRepository(db)

    def process_and_store(self, file_path: str, case_id: uuid.UUID = None, user_id: uuid.UUID = None) -> dict:
        """
        Process a PDF and store it in vector db and relational db.
        
        Args:
            file_path (str): Path to the PDF file.
            case_id (uuid.UUID, optional): ID of the case.
            user_id (uuid.UUID, optional): ID of the user.
            
        Returns:
            dict: Document metadata.
        """
        chunks = process_pdf(file_path)
        # Use a generic prefix if no case_id is provided
        prefix = f"case_{case_id}" if case_id else "public"
        collection_name = f"{prefix}_{uuid.uuid4().hex[:8]}"
        
        add_documents_to_store(chunks, collection_name)
        
        filename = os.path.basename(file_path)
        
        if case_id and user_id:
            doc = self.document_repo.create(
                filename=filename,
                case_id=case_id,
                user_id=user_id,
                collection_name=collection_name
            )
            return {
                "document_id": str(doc.id),
                "collection_name": collection_name,
                "filename": filename
            }
            
        return {
            "collection_name": collection_name,
            "filename": filename
        }
