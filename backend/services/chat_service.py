"""
Chat service.
"""

from backend.utils.gemini import call_with_fallback
from backend.prompts.chat import LEGAL_ASSISTANT_SYSTEM_PROMPT, GENERAL_HELP_SYSTEM_PROMPT

__all__ = ["ChatService"]


class ChatService:
    """Service for handling chat interactions."""

    def __init__(self) -> None:
        """Initialize the ChatService."""
        pass

    def handle_general_chat(self, query: str, history: list) -> str:
        """
        Handle a general chat query using Gemini.
        
        Args:
            query (str): The user's query.
            history (list): A list of previous message dictionaries.
            
        Returns:
            str: The AI's response.
        """
        messages = [{"role": "system", "content": GENERAL_HELP_SYSTEM_PROMPT}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": query})
        
        response = call_with_fallback(messages=messages)
        return response
