import streamlit as st
import requests
from frontend.public_ui import render_public_chatbot, render_public_lawyers, render_document_upload

API_URL = "http://127.0.0.1:8000/api"


def main():
    st.set_page_config(page_title="Legal AI", layout="wide", page_icon="⚖️")
    st.title("⚖️ AI Legal Assistant V3")
    st.caption("Powered by LangGraph · Ollama · PostgreSQL · ChromaDB")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "🏠 Home",
        "💬 Chatbot",
        "📄 Document Q&A",
        "🔍 Find Lawyers",
    ])

    if page == "🏠 Home":
        st.markdown("""
        ### Welcome to AI Legal Assistant V3
        Use the sidebar to navigate:
        - **💬 Chatbot** — Ask any legal question and get AI-powered guidance
        - **📄 Document Q&A** — Upload a PDF and ask questions about its contents
        - **🔍 Find Lawyers** — Describe your case and find the right lawyer
        """)

    elif page == "💬 Chatbot":
        render_public_chatbot()

    elif page == "📄 Document Q&A":
        render_document_upload()

    elif page == "🔍 Find Lawyers":
        render_public_lawyers()


if __name__ == "__main__":
    main()
