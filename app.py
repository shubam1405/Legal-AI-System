import streamlit as st
import requests
from frontend.public_ui import render_public_chatbot, render_public_lawyers
from frontend.agent_chat_ui import render_agent_chat

API_URL = "http://127.0.0.1:8000/api"


def main():
    st.set_page_config(page_title="Legal AI", layout="wide", page_icon="⚖️")
    st.title("⚖️ AI Legal Assistant V3")
    st.caption("Powered by LangGraph · Ollama · PostgreSQL · ChromaDB")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "🏠 Home",
        "💬 Chatbot",
        "🤖 Agent Chat (tools + PDF)",
        "🔍 Find Lawyers",
    ])

    if page == "🏠 Home":
        st.markdown("""
        ### Welcome to AI Legal Assistant V3
        Use the sidebar to navigate:
        - **💬 Chatbot** — Ask any legal question and get AI-powered guidance (also handles case lookup — try "State of Haryana v. Bhajan Lal")
        - **🤖 Agent Chat** — Tool-using agent chat; upload a judgment PDF and ask questions about it
        - **🔍 Find Lawyers** — Describe your case and find the right lawyer
        """)

    elif page == "💬 Chatbot":
        render_public_chatbot()

    elif page == "🤖 Agent Chat (tools + PDF)":
        render_agent_chat()

    elif page == "🔍 Find Lawyers":
        render_public_lawyers()


if __name__ == "__main__":
    main()
