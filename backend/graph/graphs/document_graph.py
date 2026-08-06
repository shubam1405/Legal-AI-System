from langgraph.graph import StateGraph, END, START
from backend.graph.state import LegalAssistantState
from backend.graph.nodes import ingest_document_node, document_qa_node

__all__ = ["document_graph"]

def route_doc_action(state: LegalAssistantState) -> str:
    intent = state.get("intent", "document_qa")
    if intent == "ingest":
        return "ingest_document_node"
    return "document_qa_node"

workflow = StateGraph(LegalAssistantState)
workflow.add_node("ingest_document_node", ingest_document_node)
workflow.add_node("document_qa_node", document_qa_node)

workflow.add_conditional_edges(START, route_doc_action, {
    "ingest_document_node": "ingest_document_node",
    "document_qa_node": "document_qa_node"
})

workflow.add_edge("ingest_document_node", END)
workflow.add_edge("document_qa_node", END)

document_graph = workflow.compile()
