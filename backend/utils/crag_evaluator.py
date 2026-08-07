from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

class CRAGEvaluation(BaseModel):
    is_relevant: bool = Field(
        description="True if the retrieved documents are relevant to answer the query, False otherwise."
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0 that the documents contain the answer."
    )
    reasoning: str = Field(
        description="Reasoning for the relevance and confidence score."
    )

def evaluate_retrieval(query: str, documents: List[Any], similarity_threshold: float = 0.7) -> dict:
    """
    Evaluates retrieval using similarity score (if available), relevance, and LLM confidence.
    Returns a dict with evaluation results and whether external search is needed.
    """
    if not documents:
        return {"needs_external_search": True, "reason": "No documents retrieved"}

    # Basic similarity check (if documents have a similarity score from vector store)
    # Chroma returns scores as distance, but we'll assume we have a way to check if they are close.
    # In Langchain, vectorstore.similarity_search_with_score returns (doc, score).
    # Here we just use the LLM for relevance and confidence.

    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0).with_structured_output(CRAGEvaluation)
    
    context = "\n\n".join([getattr(doc, "page_content", str(doc)) for doc in documents])
    
    prompt = f"""
    You are an evaluator for a Corrective RAG system.
    Evaluate if the following retrieved documents are relevant to the user's query and contain enough information to answer it.
    
    User Query: {query}
    
    Retrieved Documents:
    {context}
    """
    
    try:
        eval_result = llm.invoke(prompt)
        # We need both high relevance and high confidence
        if eval_result.is_relevant and eval_result.confidence >= 0.8:
            needs_external = False
        else:
            needs_external = True
            
        return {
            "needs_external_search": needs_external,
            "confidence": eval_result.confidence,
            "reason": eval_result.reasoning
        }
    except Exception as e:
        # Fallback to external search on error
        return {"needs_external_search": True, "reason": f"Evaluation failed: {str(e)}"}
