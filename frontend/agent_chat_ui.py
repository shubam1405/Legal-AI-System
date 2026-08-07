"""
Direct agent chat: talks straight to backend/legal_agent.py's tool-using
LangGraph agent (in-process, no HTTP hop), with PDF upload feeding the
same Chroma-backed tools the agent can search.

Ported from streamlit_app.py so all features live under one Streamlit
entry point (app.py). streamlit_app.py itself is left untouched and
still works standalone if run directly.
"""
import uuid

import streamlit as st
from langchain_core.messages import HumanMessage

from backend.legal_agent import build_agent
from backend.services.ingestion_service import process_pdf

__all__ = ["render_agent_chat"]


@st.cache_resource
def _load_agent():
    return build_agent()


def render_agent_chat():
    st.header("🤖 Agent Chat (tool-using, direct)")
    st.write(
        "Chats directly with the LangGraph agent — it can call tools "
        "(case search, IPC lookup) mid-conversation. Upload a judgment PDF "
        "below to let the agent search it too."
    )

    with st.spinner("Initializing Legal AI Agent..."):
        agent = _load_agent()

    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []
    if "agent_thread_id" not in st.session_state:
        st.session_state.agent_thread_id = str(uuid.uuid4())

    st.caption(f"Thread ID: `{st.session_state.agent_thread_id}`")

    uploaded_file = st.file_uploader("Upload Judgment PDF", type=["pdf"], key="agent_pdf_uploader")

    if uploaded_file:
        if st.session_state.get("agent_processed_file_id") != uploaded_file.file_id:
            with st.spinner("Processing PDF..."):
                result = process_pdf(uploaded_file, st.session_state.agent_thread_id)
            st.session_state.agent_processed_file_id = uploaded_file.file_id
            st.session_state.agent_last_process_result = result
        else:
            result = st.session_state.get("agent_last_process_result", {})

        st.success("PDF indexed successfully")
        st.json(result)

    if st.button("New Agent Chat"):
        st.session_state.agent_messages = []
        st.session_state.agent_thread_id = str(uuid.uuid4())
        st.session_state.pop("agent_processed_file_id", None)
        st.rerun()

    st.divider()

    for message in st.session_state.agent_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a legal question...", key="agent_chat_input")

    if prompt and prompt.strip():
        st.session_state.agent_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            response = agent.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config={"configurable": {"thread_id": st.session_state.agent_thread_id}},
            )
            answer = response["messages"][-1].content
        except Exception as e:
            answer = f"Error: {str(e)}"

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.agent_messages.append({"role": "assistant", "content": answer})
