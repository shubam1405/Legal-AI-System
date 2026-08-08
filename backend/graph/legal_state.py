"""
LegalState -- Pydantic state for the rebuilt public chatbot graph.

Separate from LegalAssistantState (backend/graph/state.py), which stays
untouched since document_graph and lawyer_graph both depend on it.
This state is used ONLY by the new public_graph.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

__all__ = ["LegalState"]


class LegalState(BaseModel):
    # User
    query: str

    # Intent
    intent: str = "legal_knowledge"  # SIMILAR_CASE | DIRECT_CASE_SEARCH | LEGAL_KNOWLEDGE | LEGAL_RESEARCH | CLARIFICATION
    confidence: float = 0.0

    # Extracted case information
    case_name: Optional[str] = None
    case_number: Optional[str] = None
    court: Optional[str] = None
    year: Optional[int] = None

    # For similar-case searches
    case_facts: Optional[str] = None
    search_query: Optional[str] = None

    # Retrieval
    bharat_archive_results: list = Field(default_factory=list)
    web_search_results: list = Field(default_factory=list)

    # Combined
    retrieved_cases: list = Field(default_factory=list)
    ranked_cases: list = Field(default_factory=list)

    # Final context
    context: list = Field(default_factory=list)

    # Response
    response: str = ""

    # Additions beyond the original spec
    chat_history: list = Field(default_factory=list)
    clarification_question: Optional[str] = None
    errors: list = Field(default_factory=list)
