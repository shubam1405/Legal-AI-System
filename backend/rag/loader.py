"""
Document loader using PyPDFLoader (LangChain).
"""
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.utils.exceptions import DocumentProcessingError

def process_pdf(file_path: str) -> list:
    """
    Load a PDF and split it into chunks.
    """
    if not os.path.exists(file_path):
        raise DocumentProcessingError(f"File not found: {file_path}")
        
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        return chunks
    except Exception as e:
        raise DocumentProcessingError(f"Failed to process PDF: {str(e)}")
