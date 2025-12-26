"""Home page with dashboard and statistics"""

import streamlit as st
from src.models.component import Category, ChangeType
from src.utils.database import db

def render_home():
    """Render home/dashboard page"""
    st.title("🚀 DeployTrack Low-Code")
    st.markdown("**Centralized deployment manifest for complex low-code ecosystems**")
    st.markdown("---")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    vp_components, vp_total = db.get_all_components(category=Category.VP, limit=1000)
    em_components, em_total = db.get_all_components(category=Category.EM, limit=1000)
    dm_components, dm_total = db.get_all_components(category=Category.DM, limit=1000)
    all_components, all_total = db.get_all_components(limit=1000)
    
    new_count = len([c for c in all_components if c.change_type == ChangeType.NEW])
    updated_count = len([c for c in all_components if c.change_type == ChangeType.UPDATED])
    
    with col1:
        st.metric("Total Components", all_total)
    
    with col2:
        st.metric("Visual Programming", vp_total)
    
    with col3:
        st.metric("Experience Manager", em_total)
    
    with col4:
        st.metric("Data Manager", dm_total)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🆕 New Components", new_count)
    
    with col2:
        st.metric("🔄 Updated Components", updated_count)
    
    st.markdown("---")
    
    # Quick info
    st.subheader("📖 About DeployTrack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Visual Programming (VP)**")
        st.write("Logic-heavy assets like APIs, DJOBs, and Functions")
    
    with col2:
        st.markdown("**Experience Manager (EM)**")
        st.write("Frontend and UI assets for user interfaces")
    
    with col3:
        st.markdown("**Data Manager (DM)**")
        st.write("Database schemas and data orchestration")
    
    st.markdown("---")
    
    # Recent components
    st.subheader("📅 Recent Components")
    recent, _ = db.get_all_components(limit=5)
    
    if recent:
        for comp in recent:
            change_badge = "🆕" if comp.change_type == ChangeType.NEW else "🔄"
            st.markdown(f"**{change_badge} {comp.name}** - {comp.category.value} / {comp.type} - *{comp.updated_at.strftime('%Y-%m-%d %H:%M')}*")
    else:
        st.info("No components yet. Start by adding your first deployment component!")
