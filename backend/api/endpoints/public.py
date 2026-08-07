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


from fastapi.responses import StreamingResponse
import json

import uuid

@router.post("/chat")
async def chat(request: ChatRequest) -> Any:
    """Chat with the public legal AI."""
    state = {
        "original_query": request.query,
        "chat_history": request.history,
        "language": request.language,
    }
    thread_id = f"public-chat-{uuid.uuid4()}"

    async def generate_stream():
        try:
            async for event in public_graph.astream_events(
                state,
                version="v2",
                config={"configurable": {"thread_id": thread_id}},
            ):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    # classify_intent_node also calls an LLM (for structured
                    # intent classification) inside the same graph run, which
                    # also fires on_chat_model_stream events. Only forward
                    # chunks from chat_node's own answer, or the classifier's
                    # raw JSON leaks into the response shown to the user.
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    if node_name != "chat_node":
                        continue
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        # Yield the content directly for st.write_stream to consume
                        # Or as SSE: yield f"data: {json.dumps({'chunk': chunk.content})}\n\n"
                        # Since Streamlit's write_stream expects text, we can just yield the text
                        yield chunk.content
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"\n\nError: {type(e).__name__}: {str(e)!r}"
            
    return StreamingResponse(generate_stream(), media_type="text/plain")


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
