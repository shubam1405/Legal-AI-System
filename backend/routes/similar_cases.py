from fastapi import APIRouter
from backend.services.similarity_service import get_similar_cases

router = APIRouter()


@router.get("/similar-cases")
def similar_cases(text: str):

    cases = get_similar_cases(text)

    return {
        "similar_cases": cases
    }