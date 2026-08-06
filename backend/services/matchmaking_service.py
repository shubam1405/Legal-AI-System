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
        extract_msg = [
            {"role": "system", "content": SPECIALIZATION_EXTRACTION_PROMPT},
            {"role": "user", "content": case_description}
        ]
        specializations_str = call_with_fallback(messages=extract_msg)
        
        # Parse specializations - handle various LLM output formats
        try:
            cleaned = specializations_str.strip()
            # LLM may wrap JSON in markdown code fences
            if "```" in cleaned:
                parts = cleaned.split("```")
                for part in parts:
                    part = part.strip().removeprefix("json").strip()
                    if part.startswith("["):
                        cleaned = part
                        break
            specializations = json.loads(cleaned)
            if not isinstance(specializations, list):
                specializations = [str(specializations)]
        except json.JSONDecodeError:
            # Fallback: split by comma
            specializations = [s.strip().strip('"').strip("'") for s in specializations_str.split(",")]

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
