"""Sidebar component"""

import streamlit as st
from src.utils.database import db

def render_sidebar():
    """Render sidebar navigation and API test"""
    with st.sidebar:
        st.title("📋 Navigation")
        
        page = st.radio(
            "Go to",
            [
                "🏠 Home",
                "📊 Master List",
                "⚙️ Visual Programming",
                "🎨 Experience Manager",
                "💾 Data Manager",
                "🔗 Find DM Links"
            ]
        )
        
        st.markdown("---")
        
        st.info("**DeployTrack Low-Code**\n\nTrack and manage deployment components across your low-code ecosystem.")
    
    return page
