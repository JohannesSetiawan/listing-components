"""Main application entry point"""

import streamlit as st
from src.models.component import Category
from src.components.sidebar import render_sidebar
from src.components.component_list import render_component_list
from src.pages.home import render_home
from src.pages.find_dm_links import render_find_dm_links
from src.pages.audit_trail import render_audit_trail

# Configure the page
st.set_page_config(
    page_title="DeployTrack Low-Code",
    page_icon="🚀",
    layout="wide"
)

# Initialize session state
if 'page_size' not in st.session_state:
    st.session_state.page_size = 50
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = None

def main():
    """Main application logic"""
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Route to appropriate page
    if page == "🏠 Home":
        render_home()
    
    elif page == "📊 Master List":
        render_component_list(title="📊 Master List - All Components")
    
    elif page == "⚙️ Visual Programming":
        render_component_list(category=Category.VP, title="⚙️ Visual Programming Components")
    
    elif page == "🎨 Experience Manager":
        render_component_list(category=Category.EM, title="🎨 Experience Manager Components")
    
    elif page == "💾 Data Manager":
        render_component_list(category=Category.DM, title="💾 Data Manager Components")
    
    elif page == "🔗 Find DM Links":
        render_find_dm_links()
    
    elif page == "📜 Audit Trail":
        render_audit_trail()

if __name__ == "__main__":
    main()

