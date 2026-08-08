"""
Chat service.
"""

from backend.utils.gemini import call_with_fallback, stream_with_fallback
from backend.prompts.chat import LEGAL_ASSISTANT_SYSTEM_PROMPT, GENERAL_HELP_SYSTEM_PROMPT

__all__ = ["ChatService"]


class ChatService:
    """Service for handling chat interactions."""

    def __init__(self) -> None:
        """Initialize the ChatService."""
        pass

    def _build_messages(self, query: str, history: list) -> list:
        messages = [{"role": "system", "content": GENERAL_HELP_SYSTEM_PROMPT}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": query})
        return messages

    def handle_general_chat(self, query: str, history: list) -> str:
        """
        Handle a general chat query using Gemini.
        
        Args:
            query (str): The user's query.
            history (list): A list of previous message dictionaries.
            
        Returns:
            str: The AI's response.
        """
        messages = self._build_messages(query, history)
        response = call_with_fallback(messages=messages)
        return response

    async def stream_general_chat(self, query: str, history: list, config=None):
        """
        Async-generator twin of handle_general_chat — yields response chunks
        as they stream in, instead of waiting for the full response.

        Args:
            query: The user's query.
            history: A list of previous message dictionaries.
            config: RunnableConfig from the calling LangGraph node, so
                    on_chat_model_stream events propagate correctly.
        """
        messages = self._build_messages(query, history)
        async for chunk in stream_with_fallback(messages=messages, config=config):
            yield chunk

    async def stream_response(self, query: str, context: list, history: list, config=None):
        """
        General-purpose streaming generator: like stream_general_chat, but
        with optional extra context (e.g. ranked case search results)
        injected into the prompt. Used by the rebuilt public_graph's
        response_generator node, which needs to answer either from pure
        model knowledge (context=[]) or grounded in retrieved cases
        (context=[...]).

        Args:
            query: The user's query.
            context: List of context strings (e.g. case excerpts) to ground
                     the answer in. Empty list = pure model knowledge.
            history: A list of previous message dictionaries.
            config: RunnableConfig from the calling LangGraph node.
        """
        system_prompt = GENERAL_HELP_SYSTEM_PROMPT
        if context:
            context_block = "\n\n".join(str(c) for c in context)
            system_prompt = (
                f"{GENERAL_HELP_SYSTEM_PROMPT}\n\n"
                f"Use the following retrieved case information to help answer, "
                f"and cite which case(s) you're drawing from:\n\n{context_block}"
            )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": query})

        async for chunk in stream_with_fallback(messages=messages, config=config):
            yield chunk
