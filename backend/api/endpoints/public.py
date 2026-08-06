"""
Public AI endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from backend.graph.graphs.public_graph import public_graph
from backend.services.matchmaking_service import MatchmakingService
from backend.database.database import SessionLocal

__all__ = ["router"]

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    history: list = []
    language: str = "en"


class ChatResponse(BaseModel):
    response: str


class LawyerMatchResponse(BaseModel):
    lawyers: list[dict] = []


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> Any:
    """Chat with the public legal AI."""
    try:
        state = {
            "original_query": request.query,
            "chat_history": request.history,
            "language": request.language,
        }
        result = public_graph.invoke(state)
        return ChatResponse(response=result.get("final_output", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match-lawyer", response_model=LawyerMatchResponse)
async def match_lawyer(request: ChatRequest) -> Any:
    """Find a lawyer match based on user query."""
    try:
        db = SessionLocal()
        try:
            lawyers = MatchmakingService(db).match_lawyers(request.query)
            return LawyerMatchResponse(lawyers=lawyers)
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
