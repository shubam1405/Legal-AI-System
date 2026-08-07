"""
LLM utility using Ollama (local inference).
Drop-in replacement for the previous Gemini module.

Default model: llama3.2 — change OLLAMA_MODEL in .env to override.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from backend.utils.exceptions import GeminiError  # keep same exception name for compatibility

load_dotenv()

OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

__all__ = ["get_llm", "call_with_fallback", "stream_with_fallback"]


def get_llm(temperature: float = 0.3, model: str = None) -> ChatOllama:
    """Return a ChatOllama instance."""
    return ChatOllama(
        model=model or OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
    )


def _to_lc_messages(messages: list) -> list:
    """Shared by call_with_fallback and stream_with_fallback."""
    lc_messages = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))
    return lc_messages


def call_with_fallback(prompt: str = None, messages: list = None, temperature: float = 0.3) -> str:
    """
    Call Ollama with either a plain string prompt or a list of message dicts.
    Raises GeminiError (kept for compatibility) if Ollama is unreachable.

    Args:
        prompt: Plain string prompt (used for simple single-turn calls).
        messages: List of dicts with 'role' and 'content' keys.
        temperature: Sampling temperature.
    """
    try:
        llm = get_llm(temperature=temperature)

        if messages:
            lc_messages = _to_lc_messages(messages)
            response = llm.invoke(lc_messages)
        else:
            response = llm.invoke([HumanMessage(content=prompt or "")])

        return response.content

    except Exception as e:
        raise GeminiError(
            f"Ollama call failed — is Ollama running at {OLLAMA_BASE_URL}? Error: {str(e)}"
        )


async def stream_with_fallback(prompt: str = None, messages: list = None, temperature: float = 0.3, config=None):
    """
    Async-generator twin of call_with_fallback — yields response chunks as
    they arrive from Ollama instead of returning the full string at once.

    `config` should be the LangGraph/LangChain RunnableConfig passed down
    from the calling node, so token-stream callbacks (on_chat_model_stream)
    propagate up to graph.astream_events() correctly.
    """
    llm = get_llm(temperature=temperature)
    lc_messages = _to_lc_messages(messages) if messages else [HumanMessage(content=prompt or "")]

    try:
        async for chunk in llm.astream(lc_messages, config=config):
            if chunk.content:
                yield chunk.content
    except Exception as e:
        raise GeminiError(
            f"Ollama streaming call failed — is Ollama running at {OLLAMA_BASE_URL}? Error: {str(e)}"
        )
