from typing import Any
from backend.graph.state import LegalAssistantState

__all__ = ["classify_intent_node"]

def classify_intent_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Classifies the intent if not already provided.
    """
    if state.get("intent"):
        return {}
        
    query = state.get("translated_query", state.get("original_query", "")).lower()
    intent = "chatbot"
    
    if "lawyer" in query or "find" in query or "match" in query:
        intent = "lawyer_match"
    elif "document" in query or "ingest" in query:
        intent = "document_qa"
    elif "draft" in query or "template" in query:
        intent = "legal_template"
    elif "case" in query or "analyze" in query:
        intent = "case_analysis"
    
    return {"intent": intent}
