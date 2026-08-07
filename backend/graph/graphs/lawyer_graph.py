from langgraph.graph import StateGraph, END, START
from backend.graph.state import LegalAssistantState
from backend.graph.nodes import case_analysis_node, generate_draft_node
from backend.graph.checkpoint import get_checkpointer, get_store
__all__ = ["lawyer_graph"]

def route_action(state: LegalAssistantState) -> str:
    intent = state.get("intent", "case_analysis")
    if intent == "legal_template":
        return "generate_draft_node"
    return "case_analysis_node"

workflow = StateGraph(LegalAssistantState)
workflow.add_node("case_analysis_node", case_analysis_node)
workflow.add_node("generate_draft_node", generate_draft_node)

workflow.add_conditional_edges(START, route_action, {
    "case_analysis_node": "case_analysis_node",
    "generate_draft_node": "generate_draft_node"
})

workflow.add_edge("case_analysis_node", END)
workflow.add_edge("generate_draft_node", END)

lawyer_graph = workflow.compile(checkpointer=get_checkpointer(), store=get_store())
