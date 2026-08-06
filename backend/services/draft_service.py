"""
Legal drafting service.
"""

from backend.utils.gemini import call_with_fallback
from backend.prompts.draft import DRAFT_GENERATION_PROMPT, DRAFT_REVIEW_PROMPT

__all__ = ["DraftService"]


class DraftService:
    """Service for generating and reviewing legal drafts."""

    def __init__(self) -> None:
        """Initialize the DraftService."""
        pass

    def generate_draft(self, doc_type: str, case_summary: str, instructions: str) -> str:
        """
        Generate a legal draft using Gemini.
        
        Args:
            doc_type (str): The type of document to generate.
            case_summary (str): Summary of the case.
            instructions (str): Specific instructions for the draft.
            
        Returns:
            str: The generated legal draft.
        """
        prompt_content = (
            f"Document Type: {doc_type}\n"
            f"Case Summary: {case_summary}\n"
            f"Instructions: {instructions}"
        )
        messages = [
            {"role": "system", "content": DRAFT_GENERATION_PROMPT},
            {"role": "user", "content": prompt_content}
        ]
        return call_with_fallback(messages=messages)
