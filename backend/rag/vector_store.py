"""
Vector store integration using ChromaDB + Ollama embeddings.
"""
import os
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
from backend.utils.exceptions import DatabaseError

load_dotenv()

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Use Ollama's local embedding model (nomic-embed-text is fast & accurate)
embeddings = OllamaEmbeddings(
    model=EMBED_MODEL,
    base_url=OLLAMA_BASE_URL,
)

client = PersistentClient(path=CHROMA_DB_DIR)


def get_vector_store(collection_name: str) -> Chroma:
    """Get a LangChain Chroma vector store instance."""
    try:
        return Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embeddings
        )
    except Exception as e:
        raise DatabaseError(f"Failed to connect to Chroma vector store: {str(e)}")


def add_documents_to_store(chunks: list, collection_name: str) -> None:
    """Add document chunks to a ChromaDB collection."""
    try:
        vector_store = get_vector_store(collection_name)
        vector_store.add_documents(chunks)
    except Exception as e:
        raise DatabaseError(f"Failed to add documents to Chroma store: {str(e)}")
