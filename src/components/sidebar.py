"""Sidebar component"""

import streamlit as st
from src.utils.database import db

def render_sidebar():
    """Render sidebar navigation and API test"""
    with st.sidebar:
        st.title("📋 Navigation")
        
        pages = [
            "🏠 Home",
            "📊 Master List",
            "⚙️ Visual Programming",
            "🎨 Experience Manager",
            "💾 Data Manager",
            "🔗 Find DM Links",
            "📜 Audit Trail",
            "📡 API Client"
        ]
        
        # Initialize selected_page in session state if not exists
        if 'selected_page' not in st.session_state:
            st.session_state.selected_page = "🏠 Home"
        
        # Handle migration from old page names and invalid pages
        if st.session_state.selected_page not in pages:
            # Map old page names to new ones
            if st.session_state.selected_page in ["📡 API Client - List", "📡 API Client - Detail"]:
                st.session_state.selected_page = "📡 API Client"
            else:
                st.session_state.selected_page = "🏠 Home"
        
        # Also fix nav_radio if it has old/invalid values
        if 'nav_radio' in st.session_state and st.session_state.nav_radio not in pages:
            if st.session_state.nav_radio in ["📡 API Client - List", "📡 API Client - Detail"]:
                st.session_state.nav_radio = "📡 API Client"
            else:
                st.session_state.nav_radio = st.session_state.selected_page
        
        # Sync the radio key with selected_page to handle programmatic navigation
        if 'nav_radio' not in st.session_state:
            st.session_state.nav_radio = st.session_state.selected_page
        elif st.session_state.nav_radio != st.session_state.selected_page:
            # Programmatic navigation occurred, update the radio state
            st.session_state.nav_radio = st.session_state.selected_page
        
        # Use key parameter to sync with session state
        page = st.radio(
            "Go to",
            pages,
            key="nav_radio"
        )
        
        # Update session state when user selects from radio
        st.session_state.selected_page = page
        
        st.markdown("---")
        
        st.info("**DeployTrack Low-Code**\n\nTrack and manage deployment components across your low-code ecosystem.")
    
    return page
