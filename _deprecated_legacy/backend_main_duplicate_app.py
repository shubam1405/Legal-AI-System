from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from langchain_core.messages import HumanMessage

from backend.legal_agent import build_agent
from backend.services.ingestion_service import process_pdf

import traceback

app = FastAPI()

chatbot = None


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# STARTUP
# =========================

@app.on_event("startup")
def startup():

    global chatbot

    chatbot = build_agent()

    print("Legal AI Agent initialized")


# =========================
# ROOT
# =========================

@app.get("/")
def home():

    return {"message": "Legal AI System running"}


# =========================
# CHAT
# =========================

@app.post("/chat")
def chat(query: str, thread_id: str):

    global chatbot

    try:
        response = chatbot.invoke(
            {
                "messages": [HumanMessage(content=query)]
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        return {
            "answer": response["messages"][-1].content
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


# =========================
# UPLOAD PDF
# =========================

@app.post("/upload-case")
async def upload_case(file: UploadFile, thread_id: str):

    try:
        result = process_pdf(file)
        return result
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})