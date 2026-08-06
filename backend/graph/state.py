"""
LangGraph Shared State — LegalAssistantState

Every node in every graph reads from and writes to this single TypedDict.
Each node ONLY modifies the fields it is responsible for.
"""
from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict

__all__ = ["LegalAssistantState"]


class LegalAssistantState(TypedDict, total=False):
    """
    Shared state passed between all LangGraph nodes.

    Fields are grouped by concern. Each node should document
    which fields it reads (inputs) and which it writes (outputs).

    ``total=False`` means all keys are optional at construction time,
    but nodes are expected to populate their responsible fields before
    returning.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    conversation_id: str
    """Unique ID for this conversation thread. Used for memory/checkpointing."""

    session_id: str
    """User session token from the HTTP request (for auth-aware nodes)."""

    user_id: str
    """User identifier — 'anon' for public, UUID string for authenticated users."""

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    language: str
    """
    ISO 639-1 language code detected from the original query.
    e.g. 'en', 'hi', 'ta', 'te', 'mr', 'bn'.
    Populated by: detect_language_node.
    """

    original_query: str
    """Raw user input exactly as submitted. Never modified after initial set."""

    translated_query: str
    """
    The original_query translated to English.
    If language == 'en', this equals original_query.
    Populated by: translate_query_node.
    All downstream AI nodes should use translated_query, not original_query.
    """

    # ------------------------------------------------------------------
    # Intent & Routing
    # ------------------------------------------------------------------

    intent: str
    """
    Classified intent of the user query.
    One of: chatbot | lawyer_match | document_qa | legal_template | case_analysis.
    Populated by: classify_intent_node.
    Used by: route_by_intent edge function.
    """

    current_step: str
    """
    Name of the node that is currently executing.
    Updated at the start of every node for observability.
    """

    # ------------------------------------------------------------------
    # Conversation History
    # ------------------------------------------------------------------

    messages: list[dict[str, str]]
    """
    Full message history in [{role: str, content: str}] format.
    Roles: 'user', 'assistant', 'system'.
    Appended by chatbot_node and general_help_node.
    """

    chat_history: list[dict[str, str]]
    """
    Condensed chat history for context window management.
    Last N turns. Populated from messages by chat_service.
    """

    # ------------------------------------------------------------------
    # Case Data
    # ------------------------------------------------------------------

    case_id: Optional[str]
    """UUID of the case being analyzed. Used by lawyer_graph nodes."""

    case_summary: dict[str, Any]
    """
    Structured case summary extracted by case_intake_node.
    Fields: case_type, legal_domain, summary, relevant_entities,
            jurisdiction, facts, parties, timeline, issues.
    """

    legal_domain: str
    """
    High-level legal domain of the case.
    e.g. 'Criminal Law', 'Civil Law', 'Family Law'.
    Populated by: case_intake_node.
    """

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    retrieved_chunks: list[dict[str, Any]]
    """
    Top-k document chunks retrieved from ChromaDB.
    Each chunk: {content: str, metadata: dict, score: float}.
    Populated by: document_qa_node, retrieve_laws_node.
    """

    retrieved_laws: list[dict[str, Any]]
    """
    IPC sections relevant to the case.
    Each item: {section: str, section_title: str, chapter: str, content: str, score: float}.
    Populated by: retrieve_laws_node.
    """

    retrieved_precedents: list[dict[str, Any]]
    """
    Legal precedent cases retrieved from Tavily.
    Each item: {title: str, summary: str, link: str}.
    Populated by: retrieve_precedents_node.
    """

    tool_results: dict[str, Any]
    """
    Generic bucket for any tool outputs that don't fit other fields.
    Keys are tool names, values are their raw outputs.
    """

    # ------------------------------------------------------------------
    # Lawyer Matching
    # ------------------------------------------------------------------

    matched_lawyers: list[dict[str, Any]]
    """
    Ranked lawyer profiles returned by lawyer_match_node.
    Each item: full lawyer profile dict + 'match_reasoning': str.
    Populated by: lawyer_match_node.
    """

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    uploaded_documents: list[str]
    """
    List of ChromaDB collection names for documents uploaded in this session.
    Populated by: document upload endpoint (passed into graph state).
    """

    collection_name: str
    """
    The ChromaDB collection name to query for Document QA.
    """

    document_context: str
    """
    Assembled RAG context string from retrieved_chunks.
    Built by prompt_builder.build_rag_context().
    Used directly in AI prompts.
    """

    # ------------------------------------------------------------------
    # Draft / Output
    # ------------------------------------------------------------------

    generated_draft: str
    """
    Raw legal document draft produced by generate_draft_node.
    May be revised by review_draft_node before going into final_output.
    """

    final_output: str
    """
    THE SINGLE OUTPUT FIELD for all graphs.
    Every terminal node writes here.
    After translate_response_node runs, this is in the user's language.
    The API layer reads only this field to build the HTTP response.
    """

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: dict[str, Any]
    """
    Arbitrary key-value store for observability data.
    Suggested keys: start_time, node_latencies, model_used, tokens_used.
    Never used for business logic — observability only.
    """

    errors: list[str]
    """
    Accumulated error messages from any node that caught an exception.
    Nodes must NEVER raise — catch exceptions and append here.
    The API layer checks this field to return partial results + warnings.
    """
