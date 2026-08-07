from typing import Any
from backend.graph.state import LegalAssistantState

__all__ = ["classify_intent_node"]

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from backend.schemas.intents import IntentClassification
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0).with_structured_output(IntentClassification)

def classify_intent_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Classifies the intent if not already provided using LLM structured output.
    """
    if state.get("intent"):
        return {}
        
    query = state.get("translated_query", state.get("original_query", ""))
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an intent classification system for a legal AI assistant. "
                   "Analyze the user's query and classify it into one of these categories: "
                   "'lawyer_match', 'document_qa', 'legal_template', 'case_analysis', 'case_lookup', or 'general_chat'. "
                   "If the query asks for lawyers, use 'lawyer_match'. "
                   "If it asks about uploaded documents, use 'document_qa'. "
                   "If it asks to draft or create a document, use 'legal_template'. "
                   "If it mentions precedents, similar cases, or 'v.' use 'case_lookup'. "
                   "If it asks to analyze a case, use 'case_analysis'."),
        ("user", "{query}")
    ])
    
    chain = prompt | llm
    try:
        result = chain.invoke({"query": query})
        intent = result.intent
    except Exception:
        intent = "general_chat"
    
    return {"intent": intent}
