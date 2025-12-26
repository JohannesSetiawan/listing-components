"""Component detail view"""

import streamlit as st
from src.models.component import ChangeType
from src.utils.database import db

def render_component_detail(uid):
    """Render detailed view of a component"""
    component = db.get_component_by_uid(uid)
    
    if not component:
        st.error("Component not found")
        return
    
    st.subheader(f"📋 {component.name}")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"**Component ID:** `{component.component_id}`")
        st.markdown(f"**Type:** {component.type}")
        st.markdown(f"**Category:** {component.category.value}")
    
    with col2:
        change_badge = "🆕" if component.change_type == ChangeType.NEW else "🔄"
        st.markdown(f"**Change Type:** {change_badge} {component.change_type.value}")
        st.markdown(f"**Created:** {component.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**Updated:** {component.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col3:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state.edit_mode = uid
            st.rerun()
        
        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
            if db.delete_component(uid):
                st.success("Component deleted successfully!")
                st.session_state.edit_mode = None
                st.rerun()
    
    st.markdown("---")
    
    st.markdown(f"**🔗 URL:** [{component.url_link}]({component.url_link})")
    
    if component.description:
        st.markdown("**📝 Description:**")
        st.info(component.description)
    else:
        st.info("No description provided")
