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

@app.on_event("startup")
async def on_startup() -> None:
    """
    Opens the LangGraph Postgres checkpointer's connection pool and runs
    its one-time table setup — must happen here (inside the real running
    event loop), not at import time. Then prints every registered route.
    """
    from backend.graph.checkpoint import init_persistence
    await init_persistence()

    print("\nRegistered Routes")
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if methods and path:
            for method in sorted(methods):
                if method != "HEAD":
                    print(f"{method:6} {path}")
    print()

@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint for status check."""
    return {
        "status": "ok",
        "system": "Legal AI System V3 (LangGraph + Postgres)"
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "ok"}
