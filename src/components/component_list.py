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
        from src.components.batch_import import show_import_preview
        show_import_preview()
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
                "Select": False,
                "Name": comp.name,
                "URL": comp.url_link,
                "Type": comp.type,
                "Category": comp.category.value if category is None else "",
                "Change": change_badge,
                "Description": comp.description if comp.description else "",
                "UID": comp.uid
            })
        
        df = pd.DataFrame(data)
        
        # Remove category column if filtering by category
        if category:
            df = df.drop(columns=["Category"])
        
        # Display as editable table
        st.markdown("**💡 Tip:** Double-click any cell to edit. Check boxes to select for deletion.**")
        
        # Prepare type options based on category
        if category:
            type_options = get_type_options(category)
        else:
            # For Master List, get all types from all categories
            from src.config import VP_TYPES, EM_TYPES, DM_TYPES
            type_options = VP_TYPES + EM_TYPES + DM_TYPES
        
        edited_df = st.data_editor(
            df.drop(columns=["UID"]),
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select for deletion",
                    default=False,
                ),
                "Name": st.column_config.TextColumn(
                    "Name",
                    help="Component name",
                    max_chars=200,
                    required=True
                ),
                "URL": st.column_config.LinkColumn(
                    "URL",
                    help="Direct link to the component",
                    max_chars=500,
                    required=True
                ),
                "Type": st.column_config.SelectboxColumn(
                    "Type",
                    help="Component type",
                    options=type_options,
                    required=True
                ),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    help="Component category",
                    options=["Visual Programming", "Experience Manager", "Data Manager"],
                    required=True
                ) if category is None else None,
                "Change": st.column_config.SelectboxColumn(
                    "Change",
                    help="Change type",
                    options=["🆕 New", "🔄 Updated"],
                    required=True
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    help="Component description",
                    max_chars=500
                ),
            }
        )
        
        # Mass delete functionality
        if "Select" in edited_df.columns:
            selected_rows = edited_df[edited_df["Select"] == True]
            if len(selected_rows) > 0:
                st.warning(f"⚠️ {len(selected_rows)} component(s) selected for deletion")
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button(f"🗑️ Delete {len(selected_rows)} Selected", type="secondary", use_container_width=True):
                        deleted_count = 0
                        failed_count = 0
                        
                        for idx in selected_rows.index:
                            uid = df.iloc[idx]["UID"]
                            try:
                                if db.delete_component(uid):
                                    deleted_count += 1
                                else:
                                    failed_count += 1
                            except Exception as e:
                                failed_count += 1
                        
                        if deleted_count > 0:
                            st.success(f"✅ Deleted {deleted_count} component(s)")
                        if failed_count > 0:
                            st.error(f"❌ Failed to delete {failed_count} component(s)")
                        
                        st.rerun()
        
        # Detect changes and update database (exclude Select column from change detection)
        comparison_columns = ["Select"] if "Select" in edited_df.columns else []
        if comparison_columns:
            comparison_df = edited_df.drop(columns=comparison_columns)
            original_comparison_df = df.drop(columns=["UID"] + comparison_columns)
        else:
            comparison_df = edited_df
            original_comparison_df = df.drop(columns=["UID"])
        
        if not comparison_df.equals(original_comparison_df):
            for idx, row in edited_df.iterrows():
                # Skip if selected for deletion
                if "Select" in row and row["Select"]:
                    continue
                    
                original_row = df.iloc[idx]
                uid = original_row["UID"]
                
                # Check if this row was modified
                changes_detected = False
                update_data = {}
                
                if row["Name"] != original_row["Name"]:
                    update_data["name"] = row["Name"]
                    changes_detected = True
                
                if row["URL"] != original_row["URL"]:
                    update_data["url_link"] = row["URL"]
                    changes_detected = True
                
                if row["Type"] != original_row["Type"]:
                    update_data["type"] = row["Type"]
                    changes_detected = True
                
                # Handle category change (only on Master List)
                if category is None and "Category" in row and row["Category"] != original_row["Category"]:
                    # Map category name to Category enum
                    category_map = {
                        "Visual Programming": Category.VP,
                        "Experience Manager": Category.EM,
                        "Data Manager": Category.DM
                    }
                    update_data["category"] = category_map.get(row["Category"], Category.VP)
                    changes_detected = True
                
                if row["Change"] != original_row["Change"]:
                    update_data["change_type"] = ChangeType.NEW if row["Change"] == "🆕 New" else ChangeType.UPDATED
                    changes_detected = True
                
                if row["Description"] != original_row["Description"]:
                    update_data["description"] = row["Description"]
                    changes_detected = True
                
                # Update database if changes detected
                if changes_detected:
                    try:
                        db.update_component(uid, update_data)
                        st.toast(f"✅ Updated: {row['Name']}", icon="✅")
                    except Exception as e:
                        st.error(f"Error updating {row['Name']}: {str(e)}")
        
        # Component selection for detail view
        st.markdown("---")
        st.subheader("Component Details")
        
        # Create buttons for each component
        st.markdown("**Click a component name to view details:**")
        cols_per_row = 3
        for i in range(0, len(components), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, comp in enumerate(components[i:i+cols_per_row]):
                with cols[j]:
                    if st.button(f"📄 {comp.name}", key=f"detail_{comp.uid}", use_container_width=True):
                        st.session_state.selected_component_uid = comp.uid
                        st.rerun()
        
        # Show detail view if a component is selected
        if st.session_state.get('selected_component_uid'):
            st.markdown("---")
            render_component_detail(st.session_state.selected_component_uid)
            if st.button("❌ Close Detail View"):
                st.session_state.selected_component_uid = None
                st.rerun()
        
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
