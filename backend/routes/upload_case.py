from fastapi import APIRouter, UploadFile, File
from backend.services.ingestion_service import process_pdf


router = APIRouter()


@router.post("/upload-case")
async def upload_case(file: UploadFile = File(...)):

    total_chunks = process_pdf(file)

    return {
        "message": "Case processed successfully",
        "chunks_created": total_chunks
    }