"""
Custom exception hierarchy for the Legal AI System.
All exceptions inherit from LegalAIException so callers can catch the base.
"""
from __future__ import annotations

__all__ = [
    "LegalAIException",
    "GraphExecutionError",
    "RAGRetrievalError",
    "TranslationError",
    "DatabaseError",
    "AuthenticationError",
    "DocumentProcessingError",
    "GeminiError",
]


class LegalAIException(Exception):
    """Base exception for all Legal AI errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details: dict = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


class GraphExecutionError(LegalAIException):
    """Raised when a LangGraph node fails during execution."""


class RAGRetrievalError(LegalAIException):
    """Raised when a ChromaDB similarity search fails."""


class TranslationError(LegalAIException):
    """Raised when language detection or translation fails."""


class DatabaseError(LegalAIException):
    """Raised on SQLAlchemy / PostgreSQL errors."""


class AuthenticationError(LegalAIException):
    """Raised when credentials are invalid or session has expired."""


class DocumentProcessingError(LegalAIException):
    """Raised when PDF parsing or text extraction fails."""


class GeminiError(LegalAIException):
    """Raised when all Gemini fallback models are exhausted."""
