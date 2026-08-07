from typing import Any

from backend.graph.state import LegalAssistantState
from backend.services.precedent_service import PrecedentService

__all__ = ["retrieve_precedents_node"]


def retrieve_precedents_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Looks up case precedents relevant to the user's query and writes
    them into `retrieved_precedents`, plus a formatted `final_output`
    so this node can also serve as a graph endpoint on its own.
    """
    query = state.get("translated_query", state.get("original_query", ""))
    service = PrecedentService()

    try:
        precedents = service.find_case(query)
        if not precedents:
            precedents = service.search_similar_cases(query)
    except Exception as e:
        return {"errors": state.get("errors", []) + [str(e)]}

    if not precedents:
        return {
            "retrieved_precedents": [],
            "final_output": (
                "I couldn't find any matching precedents in the indexed case documents "
                "for this query. Try uploading the relevant judgment, or rephrase your question."
            ),
        }

    lines = ["Here are the closest matching precedents I found:\n"]
    for p in precedents:
        lines.append(f"**{p['case_name']}**\n{p['excerpt']}\n")

    return {
        "retrieved_precedents": precedents,
        "final_output": "\n".join(lines),
    }
