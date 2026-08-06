from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.runnables import RunnableConfig

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool

from langchain_ollama import ChatOllama

from langgraph.checkpoint.memory import MemorySaver

from langchain_community.tools import DuckDuckGoSearchRun

from database.vector_store import find_similar_cases
from backend.state.document_store import get_current_document
from backend.tools.legal_analysis import analyze_current_case


# =========================
# GLOBALS
# =========================

llm_with_tools = None
checkpointer = None


# =========================
# TOOLS
# =========================

@tool
def summarize_current_document(config: RunnableConfig):
    """Summarize uploaded judgement."""

    thread_id = config.get("configurable", {}).get("thread_id", "default")
    text = get_current_document(thread_id)

    if not text:
        return "No document uploaded."

    return text[:2000]


@tool
def search_legal_cases(query: str):
    """
    Find similar legal precedents from the judgement database.
    """

    cases = find_similar_cases(query)

    if not cases:
        return "No similar precedents found."

    result = "Similar Legal Precedents:\n\n"

    for case, text in cases.items():

        preview = text[:400]

        result += f"Case: {case}\n"
        result += f"Relevant Extract:\n{preview}\n\n"

    return result


# Web Search Tool
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def web_search(query: str):
    """Search web for latest legal information."""
    return search_tool.run(query)


# =========================
# LLM
# =========================

llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


# =========================
# STATE
# =========================

class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]


# =========================
# CHAT NODE
# =========================

def chat_node(state: ChatState, config=None):

    system_message = SystemMessage(
        content=(
            "You are a friendly Legal AI assistant.\n\n"
            "IMPORTANT BEHAVIOR RULES:\n"
            "1. For greetings or casual messages (e.g. 'hi', 'hello', 'how are you'), "
            "respond warmly and naturally WITHOUT calling any tools. "
            "Example: 'Hi! I'm your Legal AI Assistant. How can I help you today? "
            "You can ask me about legal cases, upload a judgement for analysis, or search for legal precedents.'\n\n"
            "2. Only use tools when the user asks a clearly legal question or requests a specific action:\n"
            "   - Use 'summarize_current_document' when asked to summarize an uploaded judgement\n"
            "   - Use 'search_legal_cases' when asked to find similar cases or precedents (only with a real query)\n"
            "   - Use 'analyze_current_case' when asked to analyze a judgement\n"
            "   - Use 'web_search' when asked about recent legal news or information\n\n"
            "3. Never call a tool with an empty or vague query. If the user's intent is unclear, ask for clarification.\n\n"
            "4. Always be polite, professional, and concise."
        )
    )

    messages = [system_message, *state["messages"]]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


# =========================
# BUILD AGENT (sync)
# =========================

def build_agent():

    global llm_with_tools, checkpointer

    tools = [
        summarize_current_document,
        search_legal_cases,
        web_search,
        analyze_current_case,
    ]

    llm_with_tools = llm.bind_tools(tools)

    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")

    # tools_condition automatically routes to END when no tool is called
    graph.add_conditional_edges(
        "chat_node",
        tools_condition
    )

    graph.add_edge("tools", "chat_node")

    checkpointer = MemorySaver()

    chatbot = graph.compile(checkpointer=checkpointer)

    return chatbot


# =========================
# THREAD HELPERS
# =========================

async def retrieve_all_threads():
    """
    Return all thread ids stored in checkpoint database.
    FIX: Made async to properly await async checkpointer.list()
    """

    threads = set()

    try:

        if checkpointer is None:
            return []

        # FIX: Use async iteration
        async for checkpoint in checkpointer.alist(None):

            threads.add(
                checkpoint.config["configurable"]["thread_id"]
            )

    except Exception:
        return []

    return list(threads)