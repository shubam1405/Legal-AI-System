"""
Simplified Public Landing Page and Chatbot UI - Using only Streamlit components
"""
import streamlit as st
import json
import uuid
import time
from datetime import datetime
from pathlib import Path

from mongo_service import mongo_service
from ai_service import AIAnalysisService


def render_landing_page():
    """Render the public landing page"""
    
    # Header
    st.header(":material/balance: AI Legal Assistant")
    st.subheader("Get instant legal guidance - No registration required")
    st.divider()
    
    # Features overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### :material/chat: Legal Chatbot")
        st.write("Describe your legal issue and get AI-powered analysis instantly")
    
    with col2:
        st.write("### :material/description: Document Analysis")
        st.write("Upload your case documents and get smart insights")
    
    with col3:
        st.write("### :material/person_search: Find Lawyers")
        st.write("Connect with verified legal professionals")
    
    st.divider()
    st.subheader("Get Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(":material/chat: Chat with AI", use_container_width=True):
            st.session_state.public_page = "chatbot"
            st.rerun()
    
    with col2:
        if st.button(":material/assignment: Find Lawyers", use_container_width=True):
            st.session_state.public_page = "lawyers"
            st.rerun()
    
    with col3:
        if st.button(":material/key: Login", use_container_width=True):
            st.session_state.current_page = "auth"
            st.rerun()


def render_public_chatbot():
    """Render the public chatbot page"""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        GoogleTranslator = None
        
    st.header(":material/chat: Legal AI Chatbot")
    
    col_lang, col_back = st.columns([4, 1])
    with col_back:
        if st.button("⬅️ Back to Home", use_container_width=True):
            st.session_state.public_page = "home"
            st.rerun()

    LANGUAGES = {
        "English": "en",
        "Hindi (हिन्दी)": "hi",
        "Telugu (తెలుగు)": "te",
        "Tamil (தமிழ்)": "ta",
        "Marathi (मराठी)": "mr",
        "Bengali (বাংলা)": "bn"
    }

    with col_lang:
        selected_lang_name = st.selectbox("🌐 Select Language", list(LANGUAGES.keys()), index=0)
        target_lang = LANGUAGES[selected_lang_name]

    st.divider()

    # File uploader
    with st.expander("📎 Upload Document (Optional)"):
        uploaded_file = st.file_uploader("Upload a file for context", type=['pdf', 'txt', 'png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.success(f"{uploaded_file.name} uploaded successfully! This will be attached to your next message.")

    # Initialize chat history
    if "public_chat_history" not in st.session_state:
        st.session_state.public_chat_history = [
            {"role": "assistant", "content": "Hello! I am your AI Legal Assistant. How can I help you today?", "translations": {}}
        ]

    # Container for chat messages
    chat_container = st.container(height=400)
    
    with chat_container:
        for i, msg in enumerate(st.session_state.public_chat_history):
            with st.chat_message(msg["role"]):
                content = msg["content"]
                
                # Retrieve or fetch translation
                if target_lang != "en" and GoogleTranslator:
                    if target_lang not in msg.get("translations", {}):
                        try:
                            msg.setdefault("translations", {})[target_lang] = GoogleTranslator(source='auto', target=target_lang).translate(content)
                        except Exception:
                            msg.setdefault("translations", {})[target_lang] = content
                    content = msg["translations"].get(target_lang, content)
                
                st.markdown(content)

    # Chat input
    if prompt := st.chat_input("Type your legal question here..."):
        # Append user message
        st.session_state.public_chat_history.append({"role": "user", "content": prompt, "translations": {}})
        
        with chat_container:
            with st.chat_message("user"):
                disp_prompt = prompt
                if target_lang != "en" and GoogleTranslator:
                    try:
                        disp_prompt = GoogleTranslator(source='auto', target=target_lang).translate(prompt)
                    except:
                        pass
                st.markdown(disp_prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        # Translate query to english for the AI
                        en_prompt = prompt
                        if target_lang != "en" and GoogleTranslator:
                            try:
                                en_prompt = GoogleTranslator(source='auto', target='en').translate(prompt)
                            except:
                                en_prompt = prompt

                        # Append file context
                        context_prefix = ""
                        if uploaded_file:
                            context_prefix = f"[User attached a file named: {uploaded_file.name}. Please acknowledge it.]\n\n"

                        from ai_service import AIAnalysisService
                        ai_service = AIAnalysisService()
                        # Use conversational approach, not structured analysis
                        ai_response = ai_service.chat_about_case({}, context_prefix + en_prompt)

                        # Translate response back
                        disp_resp = ai_response
                        if target_lang != "en" and GoogleTranslator:
                            try:
                                disp_resp = GoogleTranslator(source='auto', target=target_lang).translate(ai_response)
                            except:
                                pass
                        
                        st.markdown(disp_resp)
                        
                        st.session_state.public_chat_history.append({
                            "role": "assistant",
                            "content": ai_response,
                            "translations": {target_lang: disp_resp}
                        })
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        
        st.rerun()


def render_lawyer_card(lawyer, is_match=False, match_reasoning=None):
    with st.container(border=True):
        # Header Row: Name, Rating, Badge
        rating = lawyer.get('rating', 4.0)
        reviews = lawyer.get('reviews_count', 0)
        
        header_cols = st.columns([4, 1])
        with header_cols[0]:
            is_recommended = rating >= 4.5 and lawyer.get('success_rate', 0) >= 80
            rec_badge = "🌟 **RECOMMENDED**" if is_recommended else ""
            st.markdown(f"#### 👩‍⚖️ {lawyer.get('name', 'Unknown')} &nbsp;&nbsp;|&nbsp;&nbsp; {rating}★ &nbsp;&nbsp; {rec_badge}")
            st.markdown(f"*{lawyer.get('bio', 'Legal Professional')}*")
        
        if is_match and match_reasoning:
            st.success(f"**Why Suitable:** {match_reasoning}")
            
        st.divider()
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Experience", f"{lawyer.get('experience_years', 0)} yrs")
        m2.metric("Cases Handled", f"{lawyer.get('cases_handled', 0)}")
        m3.metric("Success Rate", f"{lawyer.get('success_rate', 'N/A')}%")
        m4.metric("Reviews", f"{reviews}")
        
        st.divider()
        
        # Details: Contact vs Expertise
        d1, d2 = st.columns(2)
        
        with d1:
            st.markdown("**Contact Information**")
            st.markdown(f"📧 [{lawyer.get('email', 'N/A')}](mailto:{lawyer.get('email', '')})")
            st.markdown(f"📱 {lawyer.get('phone', 'N/A')}")
            st.markdown(f"🏢 **Firm:** {lawyer.get('firm_name', 'Independent')}")
            st.markdown(f"📍 {lawyer.get('address', lawyer.get('location', 'N/A'))}")
            st.markdown(f"⚖️ {lawyer.get('bar_council', 'Bar Council')}")
            
        with d2:
            st.markdown("**Expertise**")
            for spec in lawyer.get('specialization', []):
                st.markdown(f"🎯 {spec}")
            
            langs = ", ".join(lawyer.get('languages', ['English', 'Hindi']))
            st.markdown(f"🗣️ {langs}")
            
            courts = lawyer.get('court_types', [])
            if courts:
                st.markdown(f"🏛️ {len(courts)} court types")
                
        st.divider()
        
        # Notable cases
        st.markdown("**Notable Cases**")
        cases = lawyer.get('previous_cases', lawyer.get('past_cases', []))
        if cases:
            for case in cases:
                st.markdown(f"- {case}")
        else:
            st.markdown("- Confidential cases processed successfully.")
            
        st.divider()
        
        st.markdown("**Court Expertise**")
        if courts:
            court_cols = st.columns(len(courts) if len(courts) <= 4 else 4)
            for i, court in enumerate(courts[:4]):
                with court_cols[i]:
                    st.info(f"🏛️ {court}")
                    
        st.button("✉️ CONTACT LAWYER", key=f"contact_{lawyer.get('_id', str(id(lawyer)))}", use_container_width=True, type="primary")


def render_lawyer_card(lawyer, is_match=False, match_reasoning=None):
    with st.container(border=True):
        # Header Row: Name, Rating, Badge
        rating = lawyer.get('rating', 4.0)
        reviews = lawyer.get('reviews_count', 0)
        
        header_cols = st.columns([4, 1])
        with header_cols[0]:
            is_recommended = rating >= 4.5 and lawyer.get('success_rate', 0) >= 80
            rec_badge = "🌟 **RECOMMENDED**" if is_recommended else ""
            st.markdown(f"#### 👩‍⚖️ {lawyer.get('name', 'Unknown')} &nbsp;&nbsp;|&nbsp;&nbsp; {rating}★ &nbsp;&nbsp; {rec_badge}")
            st.markdown(f"*{lawyer.get('bio', 'Legal Professional')}*")
        
        if is_match and match_reasoning:
            st.success(f"**Why Suitable:** {match_reasoning}")
            
        st.divider()
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Experience", f"{lawyer.get('experience_years', 0)} yrs")
        m2.metric("Cases Handled", f"{lawyer.get('cases_handled', 0)}")
        m3.metric("Success Rate", f"{lawyer.get('success_rate', 'N/A')}%")
        m4.metric("Reviews", f"{reviews}")
        
        st.divider()
        
        # Details: Contact vs Expertise
        d1, d2 = st.columns(2)
        
        with d1:
            st.markdown("**Contact Information**")
            st.markdown(f"📧 [{lawyer.get('email', 'N/A')}](mailto:{lawyer.get('email', '')})")
            st.markdown(f"📱 {lawyer.get('phone', 'N/A')}")
            st.markdown(f"🏢 **Firm:** {lawyer.get('firm_name', 'Independent')}")
            st.markdown(f"📍 {lawyer.get('address', lawyer.get('location', 'N/A'))}")
            st.markdown(f"⚖️ {lawyer.get('bar_council', 'Bar Council')}")
            
        with d2:
            st.markdown("**Expertise**")
            for spec in lawyer.get('specialization', []):
                st.markdown(f"🎯 {spec}")
            
            langs = ", ".join(lawyer.get('languages', ['English', 'Hindi']))
            st.markdown(f"🗣️ {langs}")
            
            courts = lawyer.get('court_types', [])
            if courts:
                st.markdown(f"🏛️ {len(courts)} court types")
                
        st.divider()
        
        # Notable cases
        st.markdown("**Notable Cases**")
        cases = lawyer.get('previous_cases', lawyer.get('past_cases', []))
        if cases:
            for case in cases:
                st.markdown(f"- {case}")
        else:
            st.markdown("- Confidential cases processed successfully.")
            
        st.divider()
        
        st.markdown("**Court Expertise**")
        if courts:
            court_cols = st.columns(len(courts) if len(courts) <= 4 else 4)
            for i, court in enumerate(courts[:4]):
                with court_cols[i]:
                    st.info(f"🏛️ {court}")
                    
        st.button("✉️ CONTACT LAWYER", key=f"contact_{lawyer.get('_id', str(id(lawyer)))}", use_container_width=True, type="primary")

def render_public_lawyers():
    """Render the public lawyers directory"""
    st.header(":material/person_search: Find Lawyers")
    st.write("Browse verified legal professionals")
    st.divider()

    tabs = st.tabs(["Directory", "AI Matchmaker"])
    
    with tabs[0]:
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("Search by name:", placeholder="Enter lawyer name")
        with col2:
            practice_area = st.selectbox(
                "Practice Area:",
                ["All", "Civil", "Criminal", "Family", "Corporate", "Property"]
            )
        with col3:
            sort_by = st.selectbox(
                "Sort by:",
                ["Name", "Experience", "Ratings"]
            )
        st.divider()

        try:
            lawyers = mongo_service.get_all_lawyers()

            if not lawyers:
                st.info("No lawyers found in directory")
            else:
                for lawyer in lawyers:
                    if search_name and search_name.lower() not in lawyer.get('name', '').lower():
                        continue
                    if practice_area != "All" and practice_area not in lawyer.get('specialization', []):
                        continue
                        
                    render_lawyer_card(lawyer)
                    st.write("") # Spacing
        except Exception as e:
            st.error(f"Error loading lawyers: {str(e)}")

    with tabs[1]:
        st.subheader(":material/robot_2: AI Lawyer Matchmaker")
        st.write("Describe your legal issue, and our AI will find the most suitable lawyers for your case.")
        
        case_description = st.text_area("Enter your case details:", height=150)
        
        if st.button("Find Suitable Lawyers", type="primary", use_container_width=True):
            if case_description.strip():
                with st.spinner("Analyzing your case and finding the best lawyers..."):
                    try:
                        all_lawyers = mongo_service.get_all_lawyers()
                        ai_service = AIAnalysisService()
                        matched_lawyers = ai_service.suggest_lawyers_for_case(case_description, all_lawyers)
                        
                        if not matched_lawyers:
                            st.warning("No suitable lawyers found.")
                        else:
                            st.success(f"Found {len(matched_lawyers)} suitable lawyer(s)!")
                            for idx, lawyer in enumerate(matched_lawyers):
                                match_reasoning = lawyer.get('match_reasoning', 'Perfect fit for your case.')
                                render_lawyer_card(lawyer, is_match=True, match_reasoning=match_reasoning)
                                st.write("")
                    except Exception as e:
                        st.error(f"Error matching lawyers: {str(e)}")
            else:
                st.warning("Please describe your case first.")

    st.divider()

    if st.button(":material/arrow_back: Back to Home"):
        st.session_state.public_page = "home"
        st.rerun()


def render_public_navigation():
    """Render public page navigation"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Home", use_container_width=True):
            st.session_state.public_page = "home"
            st.rerun()
    
    with col2:
        if st.button("Chatbot", use_container_width=True):
            st.session_state.public_page = "chatbot"
            st.rerun()
    
    with col3:
        if st.button("Lawyers", use_container_width=True):
            st.session_state.public_page = "lawyers"
            st.rerun()
