from typing import Any, Optional
from langchain_core.runnables import RunnableConfig
from backend.graph.state import LegalAssistantState
from backend.services.chat_service import ChatService

__all__ = ["chat_node"]

async def chat_node(state: LegalAssistantState, config: Optional[RunnableConfig] = None) -> dict[str, Any]:
    """
    Handles general chat by streaming from chat_service. The underlying
    Ollama call streams token-by-token via the LangChain callback chain
    (visible to graph.astream_events() as on_chat_model_stream events),
    while this node still returns the full accumulated text as
    final_output for any non-streaming caller (e.g. graph.invoke()).
    """
    query = state.get("translated_query", state.get("original_query", ""))
    history = state.get("chat_history", [])
    chunks = []
    async for chunk in ChatService().stream_general_chat(query, history, config=config):
        chunks.append(chunk)
    return {"final_output": "".join(chunks)}
