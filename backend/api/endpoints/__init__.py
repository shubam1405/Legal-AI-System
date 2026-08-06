"""
API Endpoints package.
"""
from backend.api.endpoints.auth import router as auth_router
from backend.api.endpoints.public import router as public_router
from backend.api.endpoints.lawyer import router as lawyer_router
from backend.api.endpoints.document import router as document_router

__all__ = ["auth_router", "public_router", "lawyer_router", "document_router"]
