from backend.graph.state import LegalAssistantState

__all__ = ["route_by_intent"]

def route_by_intent(state: LegalAssistantState) -> str:
    """Routes to the next node based on intent."""
    intent = state.get("intent", "chatbot")
    if intent == "lawyer_match":
        return "lawyer_match_node"
    return "chat_node"
