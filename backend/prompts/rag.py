"""
RAG (Retrieval-Augmented Generation) prompts.
Used by rag/prompt_builder.py and legal_service.py.
"""

__all__ = ["RAG_ANSWER_PROMPT", "RAG_NO_CONTEXT_PROMPT", "IPC_ANALYSIS_PROMPT"]

RAG_ANSWER_PROMPT = """You are a precise Indian legal research assistant.

CONTEXT:
{context}

QUESTION:
{query}

Answer using ONLY the context above. Cite IPC sections or legal provisions as [Section X — Title].
If the context does not contain the answer, say plainly that the uploaded documents don't cover this — do not guess and do not speculate.

Answer:"""

RAG_NO_CONTEXT_PROMPT = """No relevant information was found in the uploaded documents for your question.

Your question: {query}

This could be because:
- The document does not contain information about this topic
- The relevant section may be in a different document
- The query may need to be rephrased

Suggestions:
1. Try rephrasing your question with different keywords
2. Upload additional relevant documents
3. Ask a more specific question about a section you know exists in the document

For general legal information about this topic, please use the main chat feature."""

IPC_ANALYSIS_PROMPT = """You are an expert in Indian Penal Code (IPC) and Indian criminal law.

Analyze the following case and the retrieved IPC sections to provide a legal assessment.

CASE FACTS:
{case_facts}

RETRIEVED IPC SECTIONS:
{ipc_context}

Provide:
1. Which retrieved IPC sections directly apply to this case and why
2. Any additional IPC sections that may apply (from your training knowledge, clearly marked as "Additional")
3. The relative seriousness of the applicable offences
4. Bail-ability of the offences
5. Recommended immediate legal steps

Format your response clearly with numbered points under each heading."""
