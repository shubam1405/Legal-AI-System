from typing import Any
from backend.graph.state import LegalAssistantState
from backend.services.document_service import DocumentService
from backend.database.database import SessionLocal

__all__ = ["ingest_document_node"]

def ingest_document_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Processes and stores a document.
    """
    # Using document_path from metadata or as a mock
    doc_path = state.get("metadata", {}).get("document_path")
    if doc_path:
        db = SessionLocal()
        try:
            result = DocumentService(db).process_and_store(doc_path)
            collection_name = result["collection_name"]
            docs = state.get("uploaded_documents", []) + [collection_name]
            return {"uploaded_documents": docs, "final_output": f"Document processed and stored in {collection_name}."}
        finally:
            db.close()
    return {"final_output": "No document path provided in metadata."}
