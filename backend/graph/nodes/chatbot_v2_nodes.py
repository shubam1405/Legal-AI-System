"""
Node functions for the rebuilt public chatbot graph (LegalState-based).

10 nodes: intent_classifier, case_query_processor, bharat_archives_search,
web_search, merge_results, rerank_cases, legal_knowledge, legal_research,
clarification, response_generator.

All nodes are async, since this graph is invoked via astream_events()
(matching the pattern used everywhere else in this project after the
checkpointer/streaming fixes).
"""
from __future__ import annotations

import os
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

from backend.graph.legal_state import LegalState
from backend.schemas.intents import ChatIntentClassification, CaseQueryExtraction
from backend.services.precedent_service import PrecedentService
from backend.services.chat_service import ChatService

__all__ = [
    "intent_classifier_node",
    "case_query_processor_node",
    "bharat_archives_search_node",
    "web_search_node",
    "merge_results_node",
    "rerank_cases_node",
    "legal_knowledge_node",
    "legal_research_node",
    "clarification_node",
    "response_generator_node",
]

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def _llm(temperature: float = 0.0):
    from langchain_ollama import ChatOllama
    return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=temperature)


# ---------------------------------------------------------------------
# 1. INTENT_CLASSIFIER
# ---------------------------------------------------------------------

async def intent_classifier_node(state: LegalState) -> dict[str, Any]:
    """Classifies into SIMILAR_CASE | DIRECT_CASE_SEARCH | LEGAL_KNOWLEDGE | LEGAL_RESEARCH | CLARIFICATION."""
    llm = _llm().with_structured_output(ChatIntentClassification)
    try:
        result = llm.invoke(
            f"Classify this legal assistant query.\n\nQuery: {state.query}"
        )
        return {"intent": result.intent, "confidence": result.confidence}
    except Exception:
        return {"intent": "LEGAL_KNOWLEDGE", "confidence": 0.0}


def route_by_intent(state: LegalState) -> str:
    intent = state.intent
    if intent in ("SIMILAR_CASE", "DIRECT_CASE_SEARCH"):
        return "case_query_processor"
    if intent == "LEGAL_RESEARCH":
        return "legal_research"
    if intent == "CLARIFICATION":
        return "clarification"
    return "legal_knowledge"  # default / LEGAL_KNOWLEDGE


# ---------------------------------------------------------------------
# 2. CASE_QUERY_PROCESSOR
# ---------------------------------------------------------------------

async def case_query_processor_node(state: LegalState) -> dict[str, Any]:
    """Extracts case_name/case_number/court/year (DIRECT_CASE_SEARCH) or
    case_facts (SIMILAR_CASE), and builds a clean search_query for both workers."""
    llm = _llm().with_structured_output(CaseQueryExtraction)
    try:
        result = llm.invoke(
            f"Extract case search details from this query.\n\nQuery: {state.query}"
        )
        return {
            "case_name": result.case_name,
            "case_number": result.case_number,
            "court": result.court,
            "year": result.year,
            "case_facts": result.case_facts,
            "search_query": result.search_query,
        }
    except Exception:
        return {"search_query": state.query}


# ---------------------------------------------------------------------
# 3 & 4. BHARAT_ARCHIVES_SEARCH / WEB_SEARCH (run in parallel, fan-out)
# ---------------------------------------------------------------------

async def bharat_archives_search_node(state: LegalState) -> dict[str, Any]:
    query = state.search_query or state.query
    try:
        results = PrecedentService().find_case(query)
        if not results:
            results = PrecedentService().search_similar_cases(query, top_k=5)
    except Exception:
        results = []
    return {"bharat_archive_results": results}


async def web_search_node(state: LegalState) -> dict[str, Any]:
    query = state.search_query or state.query
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun(region="us-en")
        raw = search.run(query)
        results = [{"source": "web_search", "excerpt": raw[:1500]}]
    except Exception:
        results = []
    return {"web_search_results": results}


# ---------------------------------------------------------------------
# 5. MERGE_RESULTS (fan-in)
# ---------------------------------------------------------------------

async def merge_results_node(state: LegalState) -> dict[str, Any]:
    combined = list(state.bharat_archive_results) + list(state.web_search_results)
    return {"retrieved_cases": combined}


# ---------------------------------------------------------------------
# 6. RERANK_CASES
# ---------------------------------------------------------------------

async def rerank_cases_node(state: LegalState) -> dict[str, Any]:
    """Reranks retrieved_cases by relevance to the query, builds final context."""
    cases = state.retrieved_cases
    if not cases:
        return {"ranked_cases": [], "context": []}

    # Cheap heuristic rerank: bharat_courts results first (verified source),
    # then web results — avoids an extra LLM call for what's usually a
    # small list (5-8 items).
    ranked = sorted(
        cases,
        key=lambda c: 0 if c.get("source") != "web_search" and "excerpt" in c else 1,
    )

    context = []
    for c in ranked:
        name = c.get("case_name", c.get("source", "result"))
        excerpt = c.get("excerpt", "")
        context.append(f"{name}: {excerpt}")

    return {"ranked_cases": ranked, "context": context}


# ---------------------------------------------------------------------
# 7. LEGAL_KNOWLEDGE (no retrieval — pure model knowledge)
# ---------------------------------------------------------------------

async def legal_knowledge_node(state: LegalState) -> dict[str, Any]:
    return {"context": []}


# ---------------------------------------------------------------------
# 8. LEGAL_RESEARCH
# ---------------------------------------------------------------------

async def legal_research_node(state: LegalState) -> dict[str, Any]:
    """
    Research-framed answer for statute/legal-concept questions.

    NOTE: this does NOT retrieve from the IPC vector store. That store
    (built by ipc_vectordb_builder.py) uses HuggingFace embeddings, while
    this project's Ollama-based retrieval elsewhere uses Ollama embeddings
    -- querying it here would hit an embedding-space mismatch and likely
    return irrelevant results. Until that's reconciled, this node
    deliberately answers from model knowledge only, same as
    legal_knowledge, just with a research-depth framing. Flagging this
    as a known simplification, not an oversight.
    """
    return {"context": []}


# ---------------------------------------------------------------------
# 9. CLARIFICATION
# ---------------------------------------------------------------------

async def clarification_node(state: LegalState) -> dict[str, Any]:
    """Generates a clarifying question and ends the turn there (no response_generator)."""
    llm = _llm(temperature=0.3)
    try:
        question = llm.invoke(
            f"The user's legal question is too vague to act on. Ask ONE short, "
            f"specific clarifying question to understand what they need.\n\n"
            f"Query: {state.query}"
        ).content
    except Exception:
        question = "Could you tell me a bit more about your legal situation?"

    return {"clarification_question": question, "response": question}


# ---------------------------------------------------------------------
# 10. RESPONSE_GENERATOR
# ---------------------------------------------------------------------

async def response_generator_node(state: LegalState, config: Optional[RunnableConfig] = None) -> dict[str, Any]:
    """
    Final answer generation. Streams via ChatService.stream_response so
    the underlying Ollama call's on_chat_model_stream events propagate
    up to the /chat endpoint's astream_events() listener.
    """
    chunks = []
    async for chunk in ChatService().stream_response(
        query=state.query,
        context=state.context,
        history=state.chat_history,
        config=config,
    ):
        chunks.append(chunk)
    return {"response": "".join(chunks)}
