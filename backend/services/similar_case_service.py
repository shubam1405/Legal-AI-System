"""
Similar Case Service.

Enforces the separation:
  - ChromaDB  → embeddings only (similarity search)
  - PostgreSQL → metadata only (structured queries, display)

When a case is indexed:
  1. The text is embedded and stored in ChromaDB ('similar_cases' collection).
  2. The metadata (case_name, court, date, etc.) is stored in PostgreSQL.
  3. The ChromaDB document ID is saved in the PG row to link the two.

When searching for similar cases:
  1. ChromaDB returns matching document IDs by vector similarity.
  2. PostgreSQL is queried by those IDs to return rich metadata.
"""
import uuid
from typing import Any

from sqlalchemy.orm import Session

from backend.database.models import SimilarCase
from backend.rag.vector_store import get_vector_store

__all__ = ["SimilarCaseService"]

SIMILAR_CASES_COLLECTION = "similar_cases"


class SimilarCaseService:
    """Service for indexing and searching similar cases."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_store = get_vector_store(SIMILAR_CASES_COLLECTION)

    def index_case(
        self,
        case_name: str,
        text: str,
        court_name: str | None = None,
        decision_date: str | None = None,
        citation: str | None = None,
        case_type: str | None = None,
        legal_domain: str | None = None,
        summary: str | None = None,
        source: str = "local_index",
        ipc_sections: list[str] | None = None,
        parties: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Index a case: embed text into ChromaDB, store metadata in PostgreSQL.

        Args:
            case_name: Title of the case (e.g. "State v. Sharma").
            text: Full text or summary to embed.
            court_name: Name of the court.
            decision_date: Date string of the decision.
            citation: Legal citation string.
            case_type: Type of case (Criminal, Civil, etc.).
            legal_domain: Legal domain.
            summary: Short summary of the case.
            source: Where this case came from.
            ipc_sections: Applicable IPC sections.
            parties: List of party names.

        Returns:
            Dict with the created case metadata.
        """
        chroma_doc_id = str(uuid.uuid4())

        # 1. Store embedding in ChromaDB ONLY
        from langchain_core.documents import Document as LCDocument

        doc = LCDocument(
            page_content=text,
            metadata={
                "chroma_doc_id": chroma_doc_id,
                "case_name": case_name,
                "source": source,
            },
        )
        self.vector_store.add_documents([doc], ids=[chroma_doc_id])

        # 2. Store metadata in PostgreSQL ONLY (no embeddings here)
        similar_case = SimilarCase(
            case_name=case_name,
            court_name=court_name,
            decision_date=decision_date,
            citation=citation,
            case_type=case_type,
            legal_domain=legal_domain,
            summary=summary or text[:500],
            source=source,
            chroma_doc_id=chroma_doc_id,
            ipc_sections=ipc_sections or [],
            parties=parties or [],
        )
        self.db.add(similar_case)
        self.db.commit()
        self.db.refresh(similar_case)

        return {
            "id": str(similar_case.id),
            "case_name": similar_case.case_name,
            "chroma_doc_id": chroma_doc_id,
            "source": source,
        }

    def search_similar(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Search for similar cases:
          1. Use ChromaDB for vector similarity search.
          2. Look up rich metadata from PostgreSQL.

        Args:
            query: The search query or case description.
            top_k: Number of results to return.

        Returns:
            List of case metadata dicts, most relevant first.
        """
        # Step 1: Vector similarity search in ChromaDB
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)

        if not docs_with_scores:
            return []

        # Step 2: Extract chroma_doc_ids from results
        chroma_ids = []
        score_map = {}
        for doc, score in docs_with_scores:
            cid = doc.metadata.get("chroma_doc_id", "")
            if cid:
                chroma_ids.append(cid)
                score_map[cid] = float(score)

        if not chroma_ids:
            return []

        # Step 3: Fetch metadata from PostgreSQL
        cases = (
            self.db.query(SimilarCase)
            .filter(SimilarCase.chroma_doc_id.in_(chroma_ids))
            .all()
        )

        # Build results preserving relevance order
        case_map = {c.chroma_doc_id: c for c in cases}
        results = []
        for cid in chroma_ids:
            case = case_map.get(cid)
            if case:
                results.append({
                    "id": str(case.id),
                    "case_name": case.case_name,
                    "court_name": case.court_name,
                    "decision_date": case.decision_date,
                    "citation": case.citation,
                    "case_type": case.case_type,
                    "legal_domain": case.legal_domain,
                    "summary": case.summary,
                    "source": case.source,
                    "ipc_sections": case.ipc_sections,
                    "parties": case.parties,
                    "similarity_score": score_map.get(cid, 0.0),
                })

        return results
