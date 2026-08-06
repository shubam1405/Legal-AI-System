from typing import Any
from backend.graph.state import LegalAssistantState
from backend.services.translation_service import translate_text

__all__ = ["translate_query_node", "translate_response_node"]

def translate_query_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Translates the original query to English if necessary.
    """
    query = state.get("original_query", "")
    language = state.get("language", "en")

    if language == "en":
        return {"translated_query": query}

    translated = translate_text(query, target_lang="en")
    return {"translated_query": translated}

def translate_response_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Translates the final output back to the user's language.
    """
    output = state.get("final_output", "")
    language = state.get("language", "en")

    if language == "en" or not output:
        return {}

    translated_output = translate_text(output, target_lang=language)
    return {"final_output": translated_output}
