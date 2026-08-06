from typing import Any
from backend.graph.state import LegalAssistantState
from backend.services.chat_service import ChatService

__all__ = ["chat_node"]

def chat_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Handles general chat by calling chat_service.
    """
    query = state.get("translated_query", state.get("original_query", ""))
    history = state.get("chat_history", [])
    response = ChatService().handle_general_chat(query, history)
    return {"final_output": response}
