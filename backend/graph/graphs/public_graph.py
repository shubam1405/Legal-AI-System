from langgraph.graph import StateGraph, END, START
from backend.graph.state import LegalAssistantState
from backend.graph.nodes import chat_node, lawyer_match_node, classify_intent_node
from backend.graph.router import route_by_intent

__all__ = ["public_graph"]

workflow = StateGraph(LegalAssistantState)
workflow.add_node("classify_intent_node", classify_intent_node)
workflow.add_node("chat_node", chat_node)
workflow.add_node("lawyer_match_node", lawyer_match_node)

workflow.add_edge(START, "classify_intent_node")
workflow.add_conditional_edges("classify_intent_node", route_by_intent, {
    "lawyer_match_node": "lawyer_match_node",
    "chat_node": "chat_node"
})
workflow.add_edge("chat_node", END)
workflow.add_edge("lawyer_match_node", END)

public_graph = workflow.compile()
