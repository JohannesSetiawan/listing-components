"""Component list with filtering and pagination"""

import streamlit as st
import pandas as pd
from src.models.component import ChangeType, Category
from src.utils.helpers import get_type_options
from src.utils.database import db
from src.components.component_form import render_component_form
from src.components.component_detail import render_component_detail
from src.components.batch_import import render_batch_import, confirm_and_import

def render_component_list(category=None, title="All Components"):
    """Render list of components with filtering and pagination"""
    st.header(title)
    
    # Filters
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        search = st.text_input("🔍 Search", placeholder="Name, ID, or description...")
    
    with col2:
        if category:
            type_options = ["All Types"] + get_type_options(category)
            type_filter = st.selectbox("Filter by Type", type_options)
            type_filter = None if type_filter == "All Types" else type_filter
        else:
            type_filter = None
    
    with col3:
        change_filter = st.selectbox("Filter by Change Type", ["All", "New", "Updated"])
    
    with col4:
        page_size = st.selectbox("Items per page", [10, 50, 100, 1000], index=1)
        st.session_state.page_size = page_size
    
    # Add new component buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➕ Add New Component", type="primary", use_container_width=True):
            st.session_state.edit_mode = "new"
            st.session_state.show_batch_import = False
            st.rerun()
    with col2:
        if st.button("📦 Batch Import", use_container_width=True):
            st.session_state.show_batch_import = True
            st.session_state.edit_mode = None
            st.rerun()
    
    st.markdown("---")
    
    # Show batch import if active
    if st.session_state.get('show_batch_import'):
        render_batch_import()
        confirm_and_import()
        st.markdown("---")
    
    # Show form if in edit/create mode
    if st.session_state.edit_mode == "new":
        render_component_form(category if category else Category.VP)
        st.markdown("---")
    elif st.session_state.edit_mode and st.session_state.edit_mode != "new":
        component = db.get_component_by_uid(st.session_state.edit_mode)
        if component:
            render_component_form(component.category, component)
        st.markdown("---")
    
    # Fetch components
    search_term = search if search else None
    components, total = db.get_all_components(
        category=category,
        type_filter=type_filter,
        search=search_term,
        limit=page_size,
        offset=st.session_state.current_page * page_size
    )
    
    # Apply change type filter
    if change_filter != "All":
        components = [c for c in components if c.change_type.value == change_filter]
        total = len(components)
    
    # Display count
    st.markdown(f"**Showing {len(components)} of {total} components**")
    
    # Display components in a table
    if components:
        data = []
        for comp in components:
            change_badge = "🆕 New" if comp.change_type == ChangeType.NEW else "🔄 Updated"
            data.append({
                "Name": comp.name,
                "Component ID": comp.component_id,
                "Type": comp.type,
                "Category": comp.category.value if category is None else "",
                "Change": change_badge,
                "Updated": comp.updated_at.strftime('%Y-%m-%d %H:%M'),
                "UID": comp.uid
            })
        
        df = pd.DataFrame(data)
        
        # Remove category column if filtering by category
        if category:
            df = df.drop(columns=["Category"])
        
        # Display as interactive table
        st.dataframe(
            df.drop(columns=["UID"]),
            use_container_width=True,
            hide_index=True
        )
        
        # Component selection for detail view
        st.markdown("---")
        st.subheader("Component Details")
        
        selected_name = st.selectbox(
            "Select a component to view details",
            options=[comp.name for comp in components],
            index=0
        )
        
        selected_comp = next((c for c in components if c.name == selected_name), None)
        if selected_comp:
            render_component_detail(selected_comp.uid)
        
        # Pagination
        total_pages = (total + page_size - 1) // page_size
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col2:
                st.markdown(f"<center>Page {st.session_state.current_page + 1} of {total_pages}</center>", unsafe_allow_html=True)
            
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.current_page >= total_pages - 1):
                    st.session_state.current_page += 1
                    st.rerun()
    else:
        st.info("No components found. Click 'Add New Component' to get started!")
