"""
Lawyer AI endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from backend.graph.graphs.lawyer_graph import lawyer_graph

__all__ = ["router"]

router = APIRouter()


class AnalyzeRequest(BaseModel):
    case_details: str


class DraftRequest(BaseModel):
    document_type: str
    case_summary: str
    instructions: str = ""


class LawyerResponse(BaseModel):
    result: str


@router.post("/analyze-case", response_model=LawyerResponse)
async def analyze_case(request: AnalyzeRequest) -> Any:
    """Analyze a legal case."""
    try:
        state = {
            "original_query": request.case_details,
            "intent": "case_analysis",
        }
        result = lawyer_graph.invoke(state)
        return LawyerResponse(result=result.get("final_output", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft-document", response_model=LawyerResponse)
async def draft_document(request: DraftRequest) -> Any:
    """Draft a legal document."""
    try:
        state = {
            "original_query": request.instructions,
            "case_summary": request.case_summary,
            "metadata": {"doc_type": request.document_type},
            "intent": "legal_template",
        }
        result = lawyer_graph.invoke(state)
        return LawyerResponse(result=result.get("final_output", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
