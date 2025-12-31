"""API Client List page - View all saved API requests"""

import streamlit as st
from src.utils.database import db
from datetime import datetime


def render_api_client_list():
    """Render the API Client List page"""
    st.title("📡 API Client - Saved Requests")
    st.markdown("**Manage your saved API requests**")
    st.markdown("---")
    
    # Add new request button
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("➕ New Request", type="primary"):
            st.session_state.api_client_selected_request = None
            st.session_state.selected_page = "📡 API Client - Detail"
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.markdown("---")
    
    # Search and filter
    search_col1, search_col2 = st.columns([2, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search by name, URL, or description...",
            label_visibility="collapsed"
        )
    
    with search_col2:
        method_filter = st.selectbox(
            "Filter by Method",
            options=["All", "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            label_visibility="collapsed"
        )
    
    # Get saved requests from database
    try:
        method_to_filter = None if method_filter == "All" else method_filter
        requests_list, total = db.get_all_api_requests(
            search=search_query if search_query else None,
            method=method_to_filter
        )
        
        if not requests_list:
            st.info("No saved requests found. Click '➕ New Request' to create one.")
            return
        
        st.write(f"**Total:** {total} request(s)")
        st.markdown("---")
        
        # Display requests as cards
        for req in requests_list:
            render_request_card(req)
            
    except Exception as e:
        st.error(f"Error loading requests: {str(e)}")


def render_request_card(req):
    """Render a single request card"""
    method_colors = {
        "GET": "🟢",
        "POST": "🟡",
        "PUT": "🟠",
        "PATCH": "🟣",
        "DELETE": "🔴",
        "HEAD": "⚪",
        "OPTIONS": "🔵"
    }
    
    method_emoji = method_colors.get(req.method, "⚫")
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### {method_emoji} **{req.name}**")
            st.markdown(f"`{req.method}` | {req.url[:80]}{'...' if len(req.url) > 80 else ''}")
            if req.description:
                st.caption(req.description[:100] + ('...' if len(req.description) > 100 else ''))
        
        with col2:
            st.caption(f"Updated: {req.updated_at.strftime('%Y-%m-%d %H:%M') if req.updated_at else 'N/A'}")
        
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("📂 Open", key=f"open_{req.uid}"):
                    st.session_state.api_client_selected_request = req.uid
                    st.session_state.selected_page = "📡 API Client - Detail"
                    st.rerun()
            
            with btn_col2:
                if st.button("🗑️", key=f"delete_{req.uid}"):
                    st.session_state.confirm_delete_request = req.uid
                    st.rerun()
        
        # Confirm delete dialog
        if st.session_state.get('confirm_delete_request') == req.uid:
            st.warning(f"Are you sure you want to delete '{req.name}'?")
            confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 3])
            
            with confirm_col1:
                if st.button("✅ Yes, Delete", key=f"confirm_del_{req.uid}"):
                    try:
                        db.delete_api_request(req.uid)
                        st.session_state.confirm_delete_request = None
                        st.success("Request deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting request: {str(e)}")
            
            with confirm_col2:
                if st.button("❌ Cancel", key=f"cancel_del_{req.uid}"):
                    st.session_state.confirm_delete_request = None
                    st.rerun()
        
        st.markdown("---")
