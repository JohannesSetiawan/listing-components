"""Sidebar component"""

import streamlit as st
from datetime import datetime
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
                "💾 Data Manager"
            ]
        )
        
        st.markdown("---")
        
        st.info("**DeployTrack Low-Code**\n\nTrack and manage deployment components across your low-code ecosystem.")
        
        # API Test
        st.markdown("---")
        if st.button("🧪 Test API"):
            response = {
                "message": "Hello World!",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success",
                "total_components": db.get_all_components(limit=1)[1]
            }
            st.json(response)
    
    return page
