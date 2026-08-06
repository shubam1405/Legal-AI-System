import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api"


def render_public_chatbot():
    st.header("💬 Legal AI Chatbot")

    if "public_chat_history" not in st.session_state:
        st.session_state.public_chat_history = [
            {"role": "assistant", "content": "Hello! I am your AI Legal Assistant. How can I help you today?"}
        ]

    chat_container = st.container(height=400)

    with chat_container:
        for msg in st.session_state.public_chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Type your legal question here..."):
        st.session_state.public_chat_history.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/public/chat",
                            json={"query": prompt, "history": st.session_state.public_chat_history[:-1]}
                        )
                        if response.status_code == 200:
                            ai_response = response.json().get("response", "No response from AI.")
                        else:
                            ai_response = f"Error: {response.status_code} - {response.text}"

                        st.markdown(ai_response)
                        st.session_state.public_chat_history.append(
                            {"role": "assistant", "content": ai_response}
                        )
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")


def render_document_upload():
    st.header("📄 Upload & Query Legal Documents")
    st.write("Upload a PDF and ask questions about its contents using AI.")

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process Document", type="primary", use_container_width=True):
            with st.spinner("Uploading and processing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(f"{API_URL}/document/upload", files=files)

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["collection_name"] = data.get("collection_name", "")
                        st.success(f"✅ Document '{data.get('filename')}' processed successfully!")
                    else:
                        st.error(f"Upload failed: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error uploading document: {str(e)}")

    st.divider()
    st.subheader("Ask a Question About Your Document")

    collection_name = st.session_state.get("collection_name", "")
    if not collection_name:
        st.info("Upload and process a document first to ask questions about it.")
    else:
        st.caption(f"📂 Active document collection: `{collection_name}`")
        query = st.text_input("Enter your question:")

        if st.button("Ask", type="primary"):
            if query.strip():
                with st.spinner("Searching document..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/document/query",
                            json={"query": query, "collection_name": collection_name}
                        )
                        if response.status_code == 200:
                            answer = response.json().get("answer", "No answer found.")
                            st.markdown(f"**Answer:** {answer}")
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Error querying document: {str(e)}")
            else:
                st.warning("Please enter a question.")


def render_lawyer_card(lawyer, is_match=False, match_reasoning=None):
    with st.container(border=True):
        rating = lawyer.get('rating', 4.0)
        st.markdown(f"#### 👩‍⚖️ {lawyer.get('name', 'Unknown')} | {rating}★")
        st.markdown(f"*{lawyer.get('bio', 'Legal Professional')}*")

        if is_match and match_reasoning:
            st.success(f"**Why Suitable:** {match_reasoning}")

        m1, m2, m3 = st.columns(3)
        m1.metric("Experience", f"{lawyer.get('experience_years', 0)} yrs")
        m2.metric("Cases Handled", f"{lawyer.get('cases_handled', 0)}")
        m3.metric("Success Rate", f"{lawyer.get('success_rate', 'N/A')}%")

        st.button("✉️ CONTACT LAWYER", key=f"contact_{lawyer.get('id', str(id(lawyer)))}", use_container_width=True, type="primary")


def render_public_lawyers():
    st.header("🔍 Find Lawyers")
    st.write("Describe your legal issue, and our AI will find the most suitable lawyers for your case.")

    case_description = st.text_area("Enter your case details:", height=150)

    if st.button("Find Suitable Lawyers", type="primary", use_container_width=True):
        if case_description.strip():
            with st.spinner("Analyzing your case and finding the best lawyers..."):
                try:
                    response = requests.post(
                        f"{API_URL}/public/match-lawyer",
                        json={"query": case_description}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        matched_lawyers = data.get("lawyers", [])

                        if not matched_lawyers:
                            st.warning("No suitable lawyers found.")
                        else:
                            st.success(f"Found {len(matched_lawyers)} suitable lawyer(s)!")
                            for lawyer in matched_lawyers:
                                render_lawyer_card(lawyer, is_match=True, match_reasoning=lawyer.get('reasoning', ''))
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error matching lawyers: {str(e)}")
        else:
            st.warning("Please describe your case first.")
