import asyncio
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage

from backend.legal_agent import build_agent
from backend.services.ingestion_service import process_pdf


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide"
)


# =====================================
# LOAD AGENT
# =====================================

@st.cache_resource
def load_agent():
    return build_agent()


with st.spinner("Initializing Legal AI Agent..."):
    chatbot = load_agent()

st.success("Legal AI Agent Loaded")


# =====================================
# SESSION STATE
# =====================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("⚖️ Legal AI System")

st.sidebar.markdown(f"Thread ID: `{st.session_state.thread_id}`")


# Upload PDF
uploaded_file = st.sidebar.file_uploader(
    "Upload Judgment PDF",
    type=["pdf"]
)

if uploaded_file:

    with st.sidebar.spinner("Processing PDF..."):
        result = process_pdf(uploaded_file, st.session_state.thread_id)

    st.sidebar.success("PDF indexed successfully")
    st.sidebar.json(result)


# Reset chat
if st.sidebar.button("New Chat"):

    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())

    st.rerun()


# =====================================
# MAIN UI
# =====================================

st.title("⚖️ Legal Research AI Assistant")

st.markdown(
    """
Ask questions about:

• Uploaded judgments  
• Similar legal precedents  
• IPC sections  
• Indian case law
"""
)

st.divider()


# =====================================
# CHAT HISTORY
# =====================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =====================================
# USER INPUT
# =====================================

prompt = st.chat_input("Ask a legal question...")

if prompt and prompt.strip():

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = chatbot.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config={
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }
        )

        messages = response["messages"]
        answer = messages[-1].content

    except Exception as e:
        answer = f"Error: {str(e)}"

    # Show assistant message
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })