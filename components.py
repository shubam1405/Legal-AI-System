"""
Simplified UI Components for AI Legal Assistant
Using only Streamlit's built-in components
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional, Any


def render_logo_section():
    """Render simple logo in sidebar"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.header(":material/balance: Legal AI")
        st.caption("Assistant v2.0")


def render_sidebar_nav_button(icon: str, label: str, key: str, callback=None):
    """Render a sidebar navigation button"""
    if st.button(f"{icon}  {label}", key=key, use_container_width=True):
        if callback:
            callback()
        return True
    return False


def render_welcome_header(username: str = "User"):
    """Render welcome header on home page"""
    st.header(f"Welcome back, {username}")


def render_matter_list(cases: List[Dict]):
    """Render cases list as simple cards"""
    if not cases:
        st.info("No cases found. Create a new matter to get started.")
        return

    for idx, case in enumerate(cases):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{case.get('title', 'Untitled')}")
                st.caption(f"Type: {case.get('case_type', 'Unknown')} • Status: {case.get('status', 'Active')}")
                if case.get('description'):
                    st.write(case.get('description')[:100] + ("..." if len(case.get('description')) > 100 else ""))
            with col2:
                # Use 'id' primarily, fallback to '_id', fallback to 'temp_{idx}' to guarantee unique keys
                case_id = case.get('id', case.get('_id', f'temp_{idx}'))
                
                if st.button("View Details", key=f"view_{case_id}_{idx}", use_container_width=True):
                    st.session_state.current_page = "case_detail"
                    st.session_state.selected_case_id = case_id
                    st.rerun()
                if st.button("Edit", key=f"edit_{case_id}_{idx}", use_container_width=True):
                    st.session_state.current_page = "case_edit"
                    st.session_state.selected_case_id = case_id
                    st.rerun()
                if st.button("Analyze", key=f"analyze_{case_id}_{idx}", use_container_width=True):
                    st.session_state.current_page = "home"
                    st.session_state.selected_case_id = case_id
                    st.session_state.action = "analyze"
                    st.rerun()

def render_case_header(title: str, reference: str, summary: str = ""):
    """Render case header"""
    st.header(title)
    if reference:
        st.caption(f"Reference: {reference}")
    if summary:
        st.info(summary)


def render_court_info(court_type: str, jurisdiction: str, case_number: str = "", hearing_date: str = ""):
    """Render court information section"""
    with st.container():
        st.subheader("Court Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Court Type:** {court_type}")
            if case_number:
                st.write(f"**Case Number:** {case_number}")
        
        with col2:
            st.write(f"**Jurisdiction:** {jurisdiction}")
            if hearing_date:
                st.write(f"**Hearing Date:** {hearing_date}")


def render_party_info(parties: List[Dict]):
    """Render party information section"""
    st.subheader("Party Information")
    
    if not parties:
        st.write("No parties identified")
        return
    
    for party in parties:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"**{party.get('role', 'Party')}:**")
        with col2:
            st.write(party.get("name", "Unknown"))


def render_tasks_section(tasks: List[Dict]):
    """Render tasks section"""
    st.subheader("Tasks")
    
    if not tasks:
        st.write("No tasks yet")
        return
    
    for task in tasks:
        status = task.get("status", "pending").lower()
        
        # Map status to color and badge
        status_colors = {
            "pending": ":material/pending:",
            "in_progress": ":material/autorenew:",
            "completed": ":material/check_circle:"
        }
        
        status_badge = status_colors.get(status, ":material/radio_button_unchecked:")
        
        col1, col2, col3 = st.columns([0.5, 3, 1])
        with col1:
            st.write(status_badge)
        with col2:
            st.write(task.get("title", task.get("description", "")))
        with col3:
            st.write(status.capitalize())


def render_document_checklist(checklist: Dict, required_docs: List[str] = None):
    """Render document checklist section"""
    st.subheader(":material/assignment: Document Checklist")
    
    # Split into included and missing
    def is_included(val):
        if isinstance(val, str):
            return val.lower() == "included"
        return bool(val)
    
    included_docs = [doc for doc, val in checklist.items() if is_included(val)]
    missing_docs = [doc for doc, val in checklist.items() if not is_included(val)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("** Included Documents:**")
        if included_docs:
            for doc in included_docs:
                st.write(f":material/check_circle: {doc}")
        else:
            st.write("No documents included yet")
    
    with col2:
        st.write("**:material/warning: Required Documents:**")
        if missing_docs:
            for doc in missing_docs:
                st.write(f":material/cancel: {doc}")
        else:
            st.write(" All required documents included!")


def render_documents_section(documents: List[Dict]):
    """Render documents section"""
    st.subheader("Documents")
    
    if not documents:
        st.write("No documents uploaded")
        return
    
    for doc in documents:
        icon = ":material/description:"
        if doc.get('file_type', '').lower() == 'pdf':
            icon = ":material/book:"
        elif doc.get('file_type', '').lower() in ['doc', 'docx']:
            icon = ":material/auto_stories:"
        
        col1, col2, col3 = st.columns([0.5, 3, 1])
        with col1:
            st.write(icon)
        with col2:
            st.write(doc.get("name", doc.get("filename", "Document")))
        with col3:
            st.write(doc.get("file_type", "").upper())


def render_ai_insights(insights: Dict):
    """Render full AI insights section with all fields"""
    st.subheader(":material/psychology: Comprehensive AI Analysis")

    if not insights:
        st.info("No insights available. Click 'Analyze Case' to generate.")
        return

    # Section 1: Overview & Strength
    st.markdown("###  :material/summarize: Case Summary")
    st.write(insights.get("summary", "No summary provided."))
    
    st.markdown("### :material/monitoring: Assessment")
    with st.container(border=True):
        st.markdown("**Case Strength:**\n\n" + str(insights.get("case_strength", "Unknown")))
        st.divider()
        confidence = insights.get("confidence_score", 0)
        st.progress(confidence / 100.0, text=f"AI Confidence: {confidence}%")

    st.divider()

    # Section 2: Parties & Details
    col_p, col_i = st.columns(2)
    with col_p:
        # Check both key_parties and parties for backward compatibility
        key_parties = insights.get("key_parties", [])
        parties = insights.get("parties", [])
        if key_parties or parties:
            with st.expander(":material/group: Key Parties", expanded=True):
                if key_parties:
                    for kp in key_parties:
                        st.markdown(f"- {kp}")
                elif parties:
                    for p in parties:
                        st.markdown(f"- **{p.get('role', 'Unknown')}:** {p.get('name', 'Unknown')}")
    
    with col_i:
        issues = insights.get("issues", [])
        if issues:
            with st.expander(":material/gavel: Legal Issues", expanded=True):
                for issue in issues:
                    st.markdown(f"- {issue}")

    # Section 3: Legal Foundation
    ipc = insights.get("ipc_sections", [])
    prec = insights.get("precedents", [])
    
    if ipc or prec:
        st.markdown("### :material/menu_book: Legal Foundation")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            if ipc:
                with st.container(border=True):
                    st.markdown("**Applicable Laws / IPC Sections**")
                    for section in ipc:
                        st.info(section)
        with col_l2:
            if prec:
                with st.container(border=True):
                    st.markdown("**Relevant Precedents**")
                    for p in prec:
                        st.success(p)
                        
    st.divider()

    # Section 4: Arguments & Risks
    col_arg, col_risk = st.columns(2)
    with col_arg:
        args = insights.get("key_arguments", [])
        themes = insights.get("themes", [])
        if args or themes:
            st.markdown("### :material/record_voice_over: Strategy")
            if themes:
                st.markdown("**Themes:** " + ", ".join(f"`{t}`" for t in themes))
            if args:
                for arg in args:
                    st.markdown(f"- {arg}")
    
    with col_risk:
        risks = insights.get("risks", [])
        errors = insights.get("potential_errors", [])
        if risks or errors:
            st.markdown("### :material/warning: Risks & Red Flags")
            if risks:
                for risk in risks:
                    st.warning(f"Risk: {risk}")
            if errors:
                for err in errors:
                    st.error(f"Potential Error: {err}")

    # Section 5: Timeline & Service Details
    timeline = insights.get("timeline", [])
    if timeline:
        st.markdown("### :material/timeline: Event Timeline")
        for event in timeline:
            date = event.get("date", "Unknown Date")
            title = event.get("title", "")
            desc = event.get("description", "")
            st.markdown(f"**{date}** — {title}")
            if desc:
                st.caption(desc)

    # Section 6: Recommendations
    recs = insights.get("recommendations", [])
    service = insights.get("service_details", "")
    
    st.divider()
    st.markdown("### :material/lightbulb: AI Recommendations & Notes")
    
    if recs:
        for rec in recs:
            st.markdown(f"- {rec}")
            
    if service:
        st.info(f"**Service Details:** {service}")


def render_timeline(timeline_events: List[Dict]):
    """Render timeline of events"""
    st.subheader("Timeline")
    
    if not timeline_events:
        st.write("No timeline events")
        return
    
    for event in timeline_events:
        with st.container():
            date = event.get("date", "")
            title = event.get("title", "")
            description = event.get("description", "")
            
            st.write(f"**{date}** - {title}")
            if description:
                st.write(f"_{description}_")


def render_upload_area():
    """Render file upload area"""
    st.subheader("Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "txt", "docx", "doc"],
        accept_multiple_files=True,
        help="Upload case documents, notices, or supporting files"
    )
    
    return uploaded_files


def render_form_field(label: str, field_type: str = "text", required: bool = False, placeholder: str = ""):
    """Render a form field"""
    required_text = " *" if required else ""
    
    if field_type == "text":
        return st.text_input(f"{label}{required_text}", placeholder=placeholder)
    
    elif field_type == "textarea":
        return st.text_area(f"{label}{required_text}", placeholder=placeholder)
    
    elif field_type == "email":
        return st.text_input(f"{label}{required_text}", placeholder=placeholder, type="default")
    
    elif field_type == "password":
        return st.text_input(f"{label}{required_text}", type="password", placeholder=placeholder)
    
    elif field_type == "select":
        return st.selectbox(f"{label}{required_text}", [""])
    
    elif field_type == "number":
        return st.number_input(f"{label}{required_text}")
    
    elif field_type == "date":
        return st.date_input(f"{label}{required_text}")
    
    return st.text_input(f"{label}{required_text}", placeholder=placeholder)


def render_empty_state(message: str = "No data available"):
    """Render empty state message"""
    st.info(message)


def format_date(date_obj: Any) -> str:
    """Format date for display"""
    if isinstance(date_obj, str):
        return date_obj
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%Y-%m-%d %H:%M")
    return str(date_obj)


def render_status_badge(status: str) -> str:
    """Return emoji badge for status"""
    status_map = {
        "pending": ":material/pending: Pending",
        "in_progress": ":material/autorenew: In Progress",
        "completed": ":material/check_circle: Completed",
        "active": ":material/check_circle: Active",
        "closed": ":material/cancel: Closed",
        "draft": ":material/description: Draft",
        "submitted": ":material/check_circle: Submitted",
    }
    return status_map.get(status.lower(), status)


def render_two_column_layout(left_content_func, right_content_func):
    """Render a two-column layout"""
    col1, col2 = st.columns(2)
    with col1:
        left_content_func()
    with col2:
        right_content_func()


def render_tabs(tabs_dict: Dict[str, callable]):
    """Render tabs with content functions
    
    Args:
        tabs_dict: Dict with {tab_name: content_function}
    """
    tab_list = st.tabs(list(tabs_dict.keys()))
    
    for tab, (tab_name, content_func) in zip(tab_list, tabs_dict.items()):
        with tab:
            content_func()


def render_section_divider():
    """Render a simple section divider"""
    st.divider()


def create_case_form_data() -> Dict:
    """Create a new case form"""
    with st.form("new_case_form"):
        st.subheader("Create New Case")
        
        title = st.text_input("Case Title *", placeholder="Enter case title")
        case_type = st.selectbox("Case Type *", ["Civil", "Criminal", "Property", "Family", "Corporate", "Other"])
        jurisdiction = st.text_input("Jurisdiction *", placeholder="Enter jurisdiction")
        court_type = st.selectbox("Court Type *", ["District", "High", "Supreme", "Revenue", "Other"])
        case_number = st.text_input("Case Number (Optional)", placeholder="Enter case number")
        
        description = st.text_area("Case Description *", placeholder="Brief description of the case")
        
        submitted = st.form_submit_button("Create Case", type="primary", use_container_width=True)
        
        if submitted:
            return {
                "title": title,
                "case_type": case_type,
                "jurisdiction": jurisdiction,
                "court_type": court_type,
                "case_number": case_number,
                "description": description,
                "submitted": True
            }
    
    return {}
