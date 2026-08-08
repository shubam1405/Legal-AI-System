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
    legal_guidance: dict = {}


from fastapi.responses import StreamingResponse
import json

import uuid

@router.post("/chat")
async def chat(request: ChatRequest) -> Any:
    """Chat with the public legal AI."""
    state = {
        "query": request.query,
        "chat_history": request.history,
    }
    thread_id = f"public-chat-{uuid.uuid4()}"

    async def generate_stream():
        try:
            streamed_any = False
            final_response = None
            async for event in public_graph.astream_events(
                state,
                version="v2",
                config={"configurable": {"thread_id": thread_id}},
            ):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    # intent_classifier / case_query_processor also call an LLM
                    # (structured output) inside the same graph run, which also
                    # fires on_chat_model_stream events. Only forward chunks from
                    # response_generator's own answer, or internal JSON leaks
                    # into the response shown to the user.
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    if node_name != "response_generator":
                        continue
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        streamed_any = True
                        yield chunk.content
                elif kind == "on_chain_end":
                    # Tracks the latest full-state output seen -- used as a
                    # fallback for paths that never reach response_generator
                    # (e.g. CLARIFICATION, which writes its own response and
                    # goes straight to END without streaming anything).
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict) and output.get("response"):
                        final_response = output["response"]

            if not streamed_any and final_response:
                yield final_response
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"\n\nError: {type(e).__name__}: {str(e)!r}"
            
    return StreamingResponse(generate_stream(), media_type="text/plain")


@router.post("/match-lawyer", response_model=LawyerMatchResponse)
async def match_lawyer(request: ChatRequest) -> Any:
    """Find a lawyer match based on user query, plus applicable legal guidance."""
    try:
        db = SessionLocal()
        try:
            service = MatchmakingService(db)
            lawyers = service.match_lawyers(request.query)
            guidance = service.get_legal_guidance(request.query)
            return LawyerMatchResponse(lawyers=lawyers, legal_guidance=guidance)
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
