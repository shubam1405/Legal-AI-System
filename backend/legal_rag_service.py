from database.vector_store import search_cases
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


def answer_question(query):

    results = search_cases(query)

    documents = results["documents"][0]

    context = "\n".join(documents)

    prompt = f"""
You are a legal assistant.

Use the legal case context below to answer the question.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    return response.content