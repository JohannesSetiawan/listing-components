"""Component form for creating and editing components"""

import streamlit as st
from src.models.component import ChangeType
from src.utils.helpers import get_type_options
from src.utils.database import db

def render_component_form(category, component=None):
    """Render form for creating or editing a component"""
    is_edit = component is not None
    
    with st.form(key=f"component_form_{category.name}"):
        st.subheader("Edit Component" if is_edit else "Add New Component")
        
        col1, col2 = st.columns(2)
        
        with col1:
            component_id = st.text_input(
                "Component ID*", 
                value=component.component_id if is_edit else "",
                help="Unique identifier from the low-code platform"
            )
            name = st.text_input(
                "Name*", 
                value=component.name if is_edit else "",
                help="Human-readable title of the component"
            )
            url_link = st.text_input(
                "URL Link*", 
                value=component.url_link if is_edit else "",
                help="Direct link to the component in the low-code editor"
            )
        
        with col2:
            type_options = get_type_options(category)
            default_type = component.type if is_edit and component.type in type_options else type_options[0]
            type_index = type_options.index(default_type) if default_type in type_options else 0
            
            comp_type = st.selectbox(
                "Type*", 
                options=type_options,
                index=type_index
            )
            
            change_type = st.selectbox(
                "Change Type*", 
                options=[ct.value for ct in ChangeType],
                index=0 if not is_edit else ([ct.value for ct in ChangeType].index(component.change_type.value) if isinstance(component.change_type, ChangeType) else 0)
            )
        
        description = st.text_area(
            "Description", 
            value=component.description if is_edit else "",
            help="Context on why the component is being deployed"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit = st.form_submit_button("💾 Save", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.session_state.edit_mode = None
            st.rerun()
        
        if submit:
            if not component_id or not name or not url_link:
                st.error("Please fill in all required fields (*)")
            else:
                component_data = {
                    'component_id': component_id,
                    'name': name,
                    'url_link': url_link,
                    'type': comp_type,
                    'change_type': ChangeType.NEW if change_type == "New" else ChangeType.UPDATED,
                    'description': description,
                    'category': category
                }
                
                try:
                    if is_edit:
                        db.update_component(component.uid, component_data)
                        st.success(f"✅ Component '{name}' updated successfully!")
                    else:
                        db.create_component(component_data)
                        st.success(f"✅ Component '{name}' added successfully!")
                    
                    st.session_state.edit_mode = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving component: {str(e)}")
