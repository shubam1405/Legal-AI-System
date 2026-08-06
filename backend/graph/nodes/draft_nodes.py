from typing import Any
from backend.graph.state import LegalAssistantState
from backend.services.draft_service import DraftService

__all__ = ["generate_draft_node"]

def generate_draft_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Generates a legal draft.
    """
    doc_type = state.get("metadata", {}).get("doc_type", "Legal Document")
    case_summary = state.get("case_summary", "")
    instructions = state.get("translated_query", state.get("original_query", ""))

    # case_summary may be a dict, convert to string if needed
    if isinstance(case_summary, dict):
        case_summary = str(case_summary)

    draft = DraftService().generate_draft(
        doc_type=doc_type,
        case_summary=case_summary,
        instructions=instructions
    )
    return {"generated_draft": draft, "final_output": draft}
