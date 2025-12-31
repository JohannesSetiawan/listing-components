"""Sidebar component"""

import streamlit as st
from src.utils.database import db

def render_sidebar():
    """Render sidebar navigation and API test"""
    with st.sidebar:
        st.title("📋 Navigation")
        
        # Get selected page from session state if exists
        default_page = st.session_state.get('selected_page', "🏠 Home")
        
        pages = [
            "🏠 Home",
            "📊 Master List",
            "⚙️ Visual Programming",
            "🎨 Experience Manager",
            "💾 Data Manager",
            "🔗 Find DM Links",
            "📜 Audit Trail",
            "📡 API Client - List",
            "📡 API Client - Detail"
        ]
        
        # Get the index of the default page
        try:
            default_index = pages.index(default_page)
        except ValueError:
            default_index = 0
        
        page = st.radio(
            "Go to",
            pages,
            index=default_index
        )
        
        # Update session state
        st.session_state.selected_page = page
        
        st.markdown("---")
        
        st.info("**DeployTrack Low-Code**\n\nTrack and manage deployment components across your low-code ecosystem.")
    
    return page
