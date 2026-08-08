"""
Document CRAG subgraph -- planner-agent pattern for answering questions
about an uploaded PDF.

    START
      |
      v
  retrieve_document        (scoped Chroma search on THIS document only)
      |
      v
  router                   (CRAG evaluator: does the doc answer it?)
      |
      +-- sufficient ------------------------------+
      |                                            v
      +-- insufficient                        generate
           |                                       ^
           v                                       |
      orchestrator  (defines the fan-out tasks)     |
           |                                        |
      +----+----+                                   |
      v         v                                   |
  bharat_worker  web_worker   <- run in parallel     |
      |         |                                    |
      +----+----+                                    |
           v                                         |
       fan_in  (both results arrive, unmerged)        |
           |                                          |
           v                                          |
       reducer  (merge + contextual-compression filter)|
           |______________________________________ ___|
                                                    v
                                                   END

Exposed to legal_agent.py as a single tool (ask_document) -- the outer
ReAct agent doesn't need to know about the fan-out complexity inside.
"""
from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langgraph.graph import StateGraph, START, END

from backend.utils.crag_evaluator import evaluate_retrieval
from database.vector_store import find_in_document
from backend.services.precedent_service import PrecedentService

__all__ = ["document_crag_graph", "run_document_crag"]


def _merge_list(existing: list, new: list) -> list:
    """Reducer for parallel branches writing to the same state key."""
    return (existing or []) + (new or [])


class DocumentCRAGState(TypedDict):
    query: str
    case_name: str  # scopes retrieval to just this uploaded document

    doc_chunks: list          # from retrieve_document
    needs_external: bool      # from router
    reason: str               # router's reasoning, for transparency

    bharat_results: Annotated[list, _merge_list]  # from bharat_worker
    web_results: Annotated[list, _merge_list]     # from web_worker

    external_context: str     # from reducer
    answer: str                # from generate


# ---------------------------------------------------------------------
# NODES
# ---------------------------------------------------------------------

def retrieve_document_node(state: DocumentCRAGState) -> dict[str, Any]:
    """Retrieve chunks from THIS document only (not the whole shared collection)."""
    try:
        chunks = find_in_document(state["query"], state["case_name"], n_results=5)
    except Exception:
        chunks = []
    return {"doc_chunks": chunks}


def router_node(state: DocumentCRAGState) -> dict[str, Any]:
    """CRAG evaluator: does the retrieved document context actually answer the query?"""
    class _Doc:
        def __init__(self, text):
            self.page_content = text

    docs = [_Doc(c) for c in state["doc_chunks"]]

    result = evaluate_retrieval(state["query"], docs)
    return {
        "needs_external": result.get("needs_external_search", True),
        "reason": result.get("reason", ""),
    }


def route_after_router(state: DocumentCRAGState) -> str:
    return "orchestrator" if state["needs_external"] else "generate"


def orchestrator_node(state: DocumentCRAGState) -> dict[str, Any]:
    """
    Defines the fan-out plan. Fixed two-task plan for now (bharat_courts +
    web search) -- kept simple rather than LLM-planned, since the two
    sources are always the same for this use case.
    """
    return {}


def bharat_worker_node(state: DocumentCRAGState) -> dict[str, Any]:
    """Worker 1: search the free bharat_courts archive."""
    try:
        results = PrecedentService().find_case(state["query"])
        if not results:
            results = PrecedentService().search_similar_cases(state["query"], top_k=3)
    except Exception:
        results = []
    return {"bharat_results": results}


def web_worker_node(state: DocumentCRAGState) -> dict[str, Any]:
    """Worker 2: general web search (DuckDuckGo, free, no API key)."""
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun(region="us-en")
        raw = search.run(state["query"])
        results = [{"source": "web_search", "excerpt": raw[:1500]}]
    except Exception:
        results = []
    return {"web_results": results}


def reducer_node(state: DocumentCRAGState) -> dict[str, Any]:
    """
    Fan-in point: both worker outputs have arrived, unmerged. This node
    combines them and applies a contextual-compression-style filter --
    discarding anything not actually relevant to the query -- via an
    LLM pass, since our external results are plain dicts, not a
    retriever's Document objects (so LangChain's
    ContextualCompressionRetriever class doesn't directly apply here).
    """
    combined = []
    for r in state.get("bharat_results", []):
        combined.append(f"[bharat_courts] {r.get('case_name', '')}: {r.get('excerpt', '')}")
    for r in state.get("web_results", []):
        combined.append(f"[web_search] {r.get('excerpt', '')}")

    if not combined:
        return {"external_context": ""}

    raw_context = "\n\n".join(combined)

    try:
        from langchain_ollama import ChatOllama
        import os
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )
        prompt = (
            "You are filtering search results down to only what's relevant.\n\n"
            f"Query: {state['query']}\n\n"
            f"Search results:\n{raw_context}\n\n"
            "Rewrite this as a short, relevant-only excerpt. Discard anything "
            "not related to the query. If nothing is relevant, say so plainly."
        )
        filtered = llm.invoke(prompt).content
    except Exception:
        filtered = raw_context  # fall back to unfiltered if the compression call fails

    return {"external_context": filtered}


def generate_node(state: DocumentCRAGState) -> dict[str, Any]:
    """
    Final generation. Uses doc context alone if sufficient (router said
    so), or doc context + external context if not -- matching the
    x+k_in / x+k_in+k_ex branching from the CRAG design.
    """
    from langchain_ollama import ChatOllama
    import os

    doc_context = "\n\n".join(state.get("doc_chunks", []))
    external_context = state.get("external_context", "")

    if external_context:
        context_block = (
            f"From the uploaded document:\n{doc_context or '(nothing relevant found)'}\n\n"
            f"From external sources (bharat_courts archive + web search):\n{external_context}"
        )
    else:
        context_block = f"From the uploaded document:\n{doc_context}"

    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3,
    )
    prompt = (
        "Answer the question using the context below. If the context includes "
        "external sources, say so in your answer so the reader knows it's not "
        "from their document.\n\n"
        f"{context_block}\n\n"
        f"Question: {state['query']}\n\nAnswer:"
    )
    answer = llm.invoke(prompt).content
    return {"answer": answer}


# ---------------------------------------------------------------------
# GRAPH
# ---------------------------------------------------------------------

_builder = StateGraph(DocumentCRAGState)
_builder.add_node("retrieve_document", retrieve_document_node)
_builder.add_node("router", router_node)
_builder.add_node("orchestrator", orchestrator_node)
_builder.add_node("bharat_worker", bharat_worker_node)
_builder.add_node("web_worker", web_worker_node)
_builder.add_node("reducer", reducer_node)
_builder.add_node("generate", generate_node)

_builder.add_edge(START, "retrieve_document")
_builder.add_edge("retrieve_document", "router")
_builder.add_conditional_edges("router", route_after_router, {
    "orchestrator": "orchestrator",
    "generate": "generate",
})

# Fan-out: orchestrator -> both workers (LangGraph runs independent
# branches like this in parallel)
_builder.add_edge("orchestrator", "bharat_worker")
_builder.add_edge("orchestrator", "web_worker")

# Fan-in: both workers -> reducer (LangGraph waits for both before running it)
_builder.add_edge("bharat_worker", "reducer")
_builder.add_edge("web_worker", "reducer")

_builder.add_edge("reducer", "generate")
_builder.add_edge("generate", END)

document_crag_graph = _builder.compile()


async def run_document_crag(query: str, case_name: str) -> dict[str, Any]:
    """Entry point for legal_agent.py's ask_document tool."""
    result = await document_crag_graph.ainvoke({"query": query, "case_name": case_name})
    return {
        "answer": result.get("answer", ""),
        "used_external": bool(result.get("external_context")),
        "reason": result.get("reason", ""),
    }
