"""
Matchmaking service.
"""

import json
from sqlalchemy.orm import Session
from backend.database.repositories.lawyer_repository import LawyerRepository
from backend.utils.gemini import call_with_fallback
from backend.prompts.lawyer_match import SPECIALIZATION_EXTRACTION_PROMPT

__all__ = ["MatchmakingService"]


class MatchmakingService:
    """Service for matching cases to appropriate lawyers."""

    def __init__(self, db: Session):
        self.db = db
        self.lawyer_repo = LawyerRepository(db)

    def match_lawyers(self, case_description: str) -> list[dict]:
        """
        Match lawyers to a case based on description.
        Returns list of lawyer dicts with full profile info.
        """
        # Step 1: Extract specializations via LLM
        from langchain_ollama import ChatOllama
        from backend.schemas.intents import LawyerSpecializationExtraction
        import os
        
        OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
        llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0).with_structured_output(LawyerSpecializationExtraction)
        
        try:
            result = llm.invoke(f"{SPECIALIZATION_EXTRACTION_PROMPT}\n\nCase description: {case_description}")
            specializations = result.specializations
        except Exception:
            specializations = []


        # Step 2: Fetch lawyers from DB
        candidates = self.lawyer_repo.search_by_specializations(specializations)
        if not candidates:
            # If no match by specialization, return all lawyers sorted by success_rate
            candidates = self.lawyer_repo.get_all()

        # Step 3: Build response dicts directly (no fragile LLM reranking)
        results = []
        for c in candidates[:5]:
            results.append({
                "id": str(c.id),
                "name": c.name,
                "specializations": c.specializations,
                "experience_years": c.experience_years,
                "cases_handled": c.cases_handled,
                "success_rate": c.success_rate,
                "rating": c.rating,
                "bio": c.bio or "",
                "firm_name": c.firm_name or "",
                "address": c.address or "",
                "phone": c.phone or "",
                "languages": c.languages,
                "court_types": c.court_types,
                "reasoning": f"Matched specializations: {', '.join(c.specializations)}. "
                             f"{c.experience_years} years experience, {c.success_rate}% success rate."
            })
        
        return results
