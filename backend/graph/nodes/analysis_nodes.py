from typing import Any
from backend.graph.state import LegalAssistantState
from backend.services.legal_service import LegalService

__all__ = ["case_analysis_node", "document_qa_node"]

def case_analysis_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Analyzes a case using legal_service.
    """
    summary = state.get("case_summary", {})
    query = state.get("translated_query", state.get("original_query", ""))
    analysis = LegalService().analyze_case(query)
    return {"final_output": analysis}

def document_qa_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Answers a query based on retrieved documents.
    """
    query = state.get("translated_query", state.get("original_query", ""))
    collection_name = state.get("collection_name", "")
    answer = LegalService().answer_document_query(query, collection_name)
    return {"final_output": answer}
