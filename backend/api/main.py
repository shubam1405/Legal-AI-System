"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from backend.api.endpoints import (
    auth_router,
    public_router,
    lawyer_router,
    document_router
)

__all__ = ["app"]

app = FastAPI(
    title="Legal AI System V3",
    description="Backend API for Legal AI System",
    version="3.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(public_router, prefix="/api/public", tags=["public"])
app.include_router(lawyer_router, prefix="/api/lawyer", tags=["lawyer"])
app.include_router(document_router, prefix="/api/document", tags=["document"])

@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint for status check."""
    return {
        "status": "ok",
        "system": "Legal AI System V3 (LangGraph + Postgres)"
    }
