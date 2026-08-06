"""
Simplified Authentication UI - Using only Streamlit components
"""
import streamlit as st
from mongo_service import mongo_service


def render_auth_page():
    """Render the login/register page"""
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo header
        st.header(":material/balance: Legal AI Assistant")
        st.caption("AI-Powered Legal Case Management")
        
        st.divider()
        
        # Tab-style login / register
        tab_login, tab_register = st.tabs(["Login", "Register"])
        
        # ==================== LOGIN TAB ====================
        with tab_login:
            st.subheader("Lawyer Login")
            
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submitted:
                if email and password:
                    result = mongo_service.authenticate_lawyer(email, password)
                    if result["success"]:
                        lawyer = result["lawyer"]
                        st.session_state.authenticated = True
                        st.session_state.lawyer_email = lawyer["email"]
                        st.session_state.lawyer_name = lawyer.get("name", "Legal Professional")
                        st.session_state.lawyer_profile = lawyer
                        
                        # Persist session
                        token = mongo_service.create_session(lawyer["email"])
                        if token:
                            st.query_params["session"] = token
                        
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Login failed"))
                else:
                    st.warning("Please enter email and password")

        # ==================== REGISTER TAB ====================
        with tab_register:
            st.subheader("New Lawyer Registration")
            
            with st.form("register_form"):
                name = st.text_input("Full Name (As per Bar Council)", placeholder="Adv. John Doe")
                email = st.text_input("Email", placeholder="your@email.com")
                bar_registration = st.text_input("Bar Council Registration No.", placeholder="e.g., D/1234/2020")
                phone = st.text_input("Phone", placeholder="+91 XXXXX XXXXX")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                
                submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
            
            if submitted:
                # Validation
                if not all([name, email, password, confirm_password]):
                    st.warning("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    # Register lawyer
                    result = mongo_service.register_lawyer(
                        name=name,
                        email=email,
                        password=password,
                        bar_registration=bar_registration,
                        phone=phone
                    )
                    
                    if result["success"]:
                        st.success("Registration successful! Please log in.")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Registration failed"))


def render_logout_button():
    """Render logout button"""
    if st.button("Logout", use_container_width=True):
        # Invalidate the server-side session token
        token = st.session_state.get("_session_token")
        if token and mongo_service.connected:
            mongo_service.delete_session(token)
        
        st.session_state.authenticated = False
        st.session_state.lawyer_email = None
        st.session_state.lawyer_name = "Legal Professional"
        st.session_state.lawyer_profile = {}
        st.session_state.current_page = "home"
        st.session_state.selected_case_id = None
        st.session_state["_session_token"] = None
        st.query_params.clear()
        st.rerun()
