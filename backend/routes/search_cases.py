from fastapi import APIRouter
from database.vector_store import search_cases

router = APIRouter()


@router.get("/search")
def search(query: str):

    results = search_cases(query)

    return results