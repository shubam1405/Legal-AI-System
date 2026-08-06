"""
Document retriever logic.
"""
from backend.rag.vector_store import get_vector_store
from backend.utils.exceptions import RAGRetrievalError
from backend.utils.logging import get_logger, log_retrieval
import time

logger = get_logger("rag_retriever")

def retrieve_context(query: str, collection_name: str, top_k: int = 5) -> str:
    """
    Retrieve relevant context from ChromaDB for a given query.
    """
    start_time = time.time()
    try:
        vector_store = get_vector_store(collection_name)
        
        # Retrieve top k documents
        docs = vector_store.similarity_search(query, k=top_k)
        
        latency = (time.time() - start_time) * 1000
        log_retrieval(logger, collection=collection_name, query=query, results_count=len(docs), latency_ms=latency)
        
        if not docs:
            return ""
            
        # Combine the text of the retrieved documents
        context = "\n\n".join([f"--- Source {i+1} ---\n{doc.page_content}" for i, doc in enumerate(docs)])
        return context
    except Exception as e:
        raise RAGRetrievalError(f"Failed to retrieve context: {str(e)}")
