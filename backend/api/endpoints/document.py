"""
Document RAG endpoints.
"""
import os
import uuid
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Any
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.graph.graphs.document_graph import document_graph

__all__ = ["router"]

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class QueryRequest(BaseModel):
    query: str
    collection_name: str


class QueryResponse(BaseModel):
    answer: str


class UploadResponse(BaseModel):
    status: str
    filename: str
    collection_name: str


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Any:
    """Upload a document for RAG ingestion."""
    try:
        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        state = {
            "metadata": {"document_path": file_path},
            "intent": "ingest",
        }
        result = await document_graph.ainvoke(
            state,
            config={"configurable": {"thread_id": f"upload-{uuid.uuid4()}"}},
        )
        collection = result.get("uploaded_documents", [file_path])[-1]
        return UploadResponse(status="success", filename=file.filename or "unknown", collection_name=str(collection))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi.responses import StreamingResponse

@router.post("/query")
async def query_document(request: QueryRequest) -> Any:
    """Query ingested documents using RAG."""
    state = {
        "original_query": request.query,
        "collection_name": request.collection_name,
        "intent": "document_qa",
    }
    
    async def generate_stream():
        try:
            async for event in document_graph.astream_events(
                state,
                version="v2",
                config={"configurable": {"thread_id": request.collection_name}},
            ):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        yield chunk.content
        except Exception as e:
            yield f"\n\nError: {str(e)}"
            
    return StreamingResponse(generate_stream(), media_type="text/plain")
