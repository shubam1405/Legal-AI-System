from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from backend.legal_agent import chatbot

router = APIRouter()


@router.get("/chat")
async def chat(query: str):

    result = await chatbot.ainvoke(
        {
            "messages": [HumanMessage(content=query)]
        }
    )

    return {
        "answer": result["messages"][-1].content
    }