from langgraph.graph import StateGraph, END, START
from backend.graph.legal_state import LegalState
from backend.graph.nodes.chatbot_v2_nodes import (
    intent_classifier_node,
    case_query_processor_node,
    bharat_archives_search_node,
    web_search_node,
    merge_results_node,
    rerank_cases_node,
    legal_knowledge_node,
    legal_research_node,
    clarification_node,
    response_generator_node,
    route_by_intent,
)
from backend.graph.checkpoint import get_checkpointer, get_store

__all__ = ["public_graph"]

workflow = StateGraph(LegalState)

workflow.add_node("intent_classifier", intent_classifier_node)
workflow.add_node("case_query_processor", case_query_processor_node)
workflow.add_node("bharat_archives_search", bharat_archives_search_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("merge_results", merge_results_node)
workflow.add_node("rerank_cases", rerank_cases_node)
workflow.add_node("legal_knowledge", legal_knowledge_node)
workflow.add_node("legal_research", legal_research_node)
workflow.add_node("clarification", clarification_node)
workflow.add_node("response_generator", response_generator_node)

workflow.add_edge(START, "intent_classifier")

workflow.add_conditional_edges("intent_classifier", route_by_intent, {
    "case_query_processor": "case_query_processor",
    "legal_knowledge": "legal_knowledge",
    "legal_research": "legal_research",
    "clarification": "clarification",
})

# Fan-out: case_query_processor -> both search sources, always both, in parallel
workflow.add_edge("case_query_processor", "bharat_archives_search")
workflow.add_edge("case_query_processor", "web_search")

# Fan-in: both sources -> merge_results
workflow.add_edge("bharat_archives_search", "merge_results")
workflow.add_edge("web_search", "merge_results")

workflow.add_edge("merge_results", "rerank_cases")
workflow.add_edge("rerank_cases", "response_generator")

workflow.add_edge("legal_knowledge", "response_generator")
workflow.add_edge("legal_research", "response_generator")

# Clarification writes its own response and ends the turn directly
workflow.add_edge("clarification", END)

workflow.add_edge("response_generator", END)

public_graph = workflow.compile(checkpointer=get_checkpointer(), store=get_store())
