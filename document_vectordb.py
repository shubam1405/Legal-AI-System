"""
Document Vector Database - Store and search vectors for user-uploaded documents
Simplified implementation to avoid dependency conflicts
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib


class DocumentVectorDB:
    """Simple document storage for user-uploaded documents"""
    
    def __init__(self, persist_dir: str = None, session_id: str = None):
        """
        Initialize the document database
        
        Args:
            persist_dir: Directory to persist documents
            session_id: Session ID for organizing documents
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.persist_dir = persist_dir or os.path.join("data", "user_documents")
        self.documents_file = os.path.join(self.persist_dir, f"documents_{self.session_id}.json")
        
        os.makedirs(self.persist_dir, exist_ok=True)
        self.documents = self._load_documents()
    
    def _load_documents(self) -> Dict[str, Any]:
        """Load documents from disk"""
        if os.path.exists(self.documents_file):
            try:
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"documents": []}
    
    def _save_documents(self):
        """Save documents to disk"""
        try:
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving documents: {e}")
    
    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a document to the database
        
        Args:
            doc_id: Unique document ID
            content: Full text content of the document
            metadata: Additional metadata
        
        Returns:
            True if successful
        """
        try:
            if not content or len(content.strip()) == 0:
                return False
            
            # Create doc entry
            doc_entry = {
                "id": doc_id,
                "content": content,
                "metadata": metadata or {},
                "hash": hashlib.md5(content.encode()).hexdigest(),
                "created_at": datetime.now().isoformat(),
                "tokens": len(content.split())
            }
            
            # Check if document already exists
            existing = [d for d in self.documents["documents"] if d["id"] == doc_id]
            if existing:
                # Update existing
                idx = self.documents["documents"].index(existing[0])
                self.documents["documents"][idx] = doc_entry
            else:
                # Add new
                self.documents["documents"].append(doc_entry)
            
            self._save_documents()
            return True
        
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search documents by keyword matching
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of matching documents with scores
        """
        if not query or len(query.strip()) == 0:
            return []
        
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents.get("documents", []):
            content_lower = doc["content"].lower()
            
            # Count keyword matches
            matches = sum(1 for word in query_words if word in content_lower)
            
            if matches > 0:
                # Simple relevance score
                score = matches / len(query_words) if query_words else 0
                results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": score
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        for doc in self.documents.get("documents", []):
            if doc["id"] == doc_id:
                return doc
        return None
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document"""
        original_count = len(self.documents["documents"])
        self.documents["documents"] = [
            d for d in self.documents["documents"] 
            if d["id"] != doc_id
        ]
        
        if len(self.documents["documents"]) < original_count:
            self._save_documents()
            return True
        return False
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        return self.documents.get("documents", [])
    
    def clear(self):
        """Clear all documents"""
        self.documents = {"documents": []}
        self._save_documents()
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Get list of all documents with metadata"""
        return [
            {
                "id": d["id"],
                "filename": d["metadata"].get("filename", "document"),
                "created_at": d["created_at"],
                "tokens": d["tokens"]
            }
            for d in self.documents.get("documents", [])
        ]

