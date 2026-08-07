from typing import Any
from backend.graph.state import LegalAssistantState
from backend.services.legal_service import LegalService

__all__ = ["case_analysis_node", "document_qa_node"]

def case_analysis_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Analyzes a case using legal_service.
    """
    summary = state.get("case_summary", {})
    query = state.get("translated_query", state.get("original_query", ""))
    analysis = LegalService().analyze_case(query)
    return {"final_output": analysis}

def document_qa_node(state: LegalAssistantState) -> dict[str, Any]:
    """
    Answers a query based on retrieved documents, using CRAG evaluation.
    """
    query = state.get("translated_query", state.get("original_query", ""))
    collection_name = state.get("collection_name", "")
    
    # 1. Retrieve documents
    from backend.rag.vector_store import get_vector_store
    from backend.utils.crag_evaluator import evaluate_retrieval
    from backend.services.retrieval_service import get_retrieval_chain
    
    try:
        retriever = get_vector_store(collection_name).as_retriever()
        docs = retriever.invoke(query)
        
        # 2. Evaluate retrieval (CRAG)
        eval_result = evaluate_retrieval(query, docs)
        
        if eval_result.get("needs_external_search"):
            # Trigger external search (fallback mechanism)
            # In a full implementation, you'd perform a web search here
            pass
            
        # 3. Answer using modern retrieval chain
        chain = get_retrieval_chain(collection_name)
        # We invoke the chain (in streaming setup, this would be an astream, but for now invoke)
        result = chain.invoke({
            "input": query,
            "chat_history": state.get("chat_history", [])
        })
        answer = result.get("answer", "No answer generated.")
        return {"final_output": answer}
    except Exception as e:
        return {"final_output": f"Error answering document query: {str(e)}"}

