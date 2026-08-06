from typing import Any
from backend.graph.state import LegalAssistantState
from backend.services.matchmaking_service import MatchmakingService
from backend.database.database import SessionLocal

__all__ = ["lawyer_match_node"]

def lawyer_match_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Finds matching lawyers based on the query or case summary.
    """
    query = state.get("translated_query", state.get("original_query", ""))
    lawyers = MatchmakingService(SessionLocal()).match_lawyers(query)
    
    output = "Here are the matched lawyers:\n"
    for l in lawyers:
        output += f"- {l.get('name', 'Unknown')}: {l.get('match_reasoning', '')}\n"
        
    return {"matched_lawyers": lawyers, "final_output": output}
