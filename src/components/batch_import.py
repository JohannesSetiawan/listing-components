"""Batch import component for importing multiple components at once"""

import streamlit as st
import re
from src.models.component import Category, ChangeType
from src.utils.database import db
from src.config import VP_TYPES, EM_TYPES, DM_TYPES

def parse_batch_import(text):
    """
    Parse batch import text and extract component information
    
    Format examples:
    - [IMPORT] [FUNCTION] ACCRUE IMPORT VALIDATION https://<base>/#/visual-programming/hadiUc1Vg
    - [accrue][creation] ui creation detail https://<base>/#/experience-manager/update/5smJ6oH4R
    - Table name https://<base>/#/form-data/table/group123/componentId456
    """
    lines = text.strip().split('\n')
    components = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Find URL in the line
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, line)
        
        if not url_match:
            continue
        
        url = url_match.group(0)
        
        # Extract name (everything before URL, trimmed)
        name = line[:url_match.start()].strip()
        if not name:
            name = "Untitled Component"
        
        # Parse URL to determine category and extract component ID
        component_data = None
        
        # Visual Programming pattern: /#/visual-programming/<component-id>
        vp_match = re.search(r'/#/visual-programming/([^/\s?#]+)', url)
        if vp_match:
            component_id = vp_match.group(1)
            component_data = {
                'name': name,
                'component_id': component_id,
                'url_link': url,
                'category': Category.VP,
                'type': VP_TYPES[0],  # Default to first type (API)
                'change_type': ChangeType.NEW,
                'description': ''
            }
        
        # Experience Manager pattern: /#/experience-manager/update/<component-id>
        em_match = re.search(r'/#/experience-manager/update/([^/\s?#]+)', url)
        if em_match:
            component_id = em_match.group(1)
            component_data = {
                'name': name,
                'component_id': component_id,
                'url_link': url,
                'category': Category.EM,
                'type': EM_TYPES[0],  # Default to first type (Single UI)
                'change_type': ChangeType.NEW,
                'description': ''
            }
        
        # Data Manager pattern: /#/form-data/table/<group_id>/<component-id>
        dm_match = re.search(r'/#/form-data/table/([^/\s?#]+)/([^/\s?#]+)', url)
        if dm_match:
            group_id = dm_match.group(1)
            component_id = dm_match.group(2)
            component_data = {
                'name': name,
                'component_id': component_id,
                'url_link': url,
                'category': Category.DM,
                'type': DM_TYPES[0],  # Default to first type (Schema)
                'change_type': ChangeType.NEW,
                'description': f'Group ID: {group_id}'
            }
        
        if component_data:
            components.append(component_data)
    
    return components

def render_batch_import():
    """Render batch import interface"""
    st.subheader("📦 Batch Import Components")
    
    st.markdown("""
    **Import multiple components at once!**
    
    Paste your component list below. Each line should contain:
    - Component name (optional) followed by the URL
    
    **Supported URL formats:**
    - Visual Programming: `https://<base>/#/visual-programming/<component-id>`
    - Experience Manager: `https://<base>/#/experience-manager/update/<component-id>`
    - Data Manager: `https://<base>/#/form-data/table/<group_id>/<component-id>`
    """)
    
    with st.form("batch_import_form"):
        import_text = st.text_area(
            "Paste your component list here",
            height=300,
            placeholder="""Example:
[IMPORT] [FUNCTION] ACCRUE IMPORT VALIDATION https://example.com/#/visual-programming/hadiUc1Vg
Dedicated Job Accrue Top Up Integration https://example.com/#/visual-programming/CV5dU4ONR
[accrue][creation] ui creation detail https://example.com/#/experience-manager/update/5smJ6oH4R
Table Schema https://example.com/#/form-data/table/group123/table456"""
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submit = st.form_submit_button("📥 Import Components", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.session_state.show_batch_import = False
            st.rerun()
        
        if submit:
            if not import_text.strip():
                st.error("Please paste at least one component to import")
            else:
                # Parse the input
                parsed_components = parse_batch_import(import_text)
                
                if not parsed_components:
                    st.error("No valid components found. Please check your URL format.")
                else:
                    # Show preview
                    st.success(f"✅ Found {len(parsed_components)} component(s) to import")
                    
                    # Display preview in expandable sections
                    with st.expander("📋 Preview Components", expanded=True):
                        for i, comp_data in enumerate(parsed_components, 1):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.markdown(f"**{i}. {comp_data['name']}**")
                                st.caption(f"ID: `{comp_data['component_id']}`")
                            with col2:
                                st.markdown(f"**Category:** {comp_data['category'].value}")
                            with col3:
                                st.markdown(f"**Type:** {comp_data['type']}")
                            
                            if comp_data['description']:
                                st.caption(f"Description: {comp_data['description']}")
                            st.markdown("---")
                    
                    # Import button (outside the form)
                    st.session_state.pending_imports = parsed_components
                    st.session_state.show_import_confirmation = True

def confirm_and_import():
    """Show confirmation and execute import"""
    if 'pending_imports' in st.session_state and st.session_state.get('show_import_confirmation'):
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("✅ Confirm Import", type="primary", use_container_width=True):
                success_count = 0
                error_count = 0
                errors = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, comp_data in enumerate(st.session_state.pending_imports):
                    try:
                        db.create_component(comp_data)
                        success_count += 1
                        status_text.text(f"Importing {i+1}/{len(st.session_state.pending_imports)}: {comp_data['name']}")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"{comp_data['name']}: {str(e)}")
                    
                    progress_bar.progress((i + 1) / len(st.session_state.pending_imports))
                
                progress_bar.empty()
                status_text.empty()
                
                # Show results
                if success_count > 0:
                    st.success(f"🎉 Successfully imported {success_count} component(s)!")
                
                if error_count > 0:
                    st.error(f"❌ Failed to import {error_count} component(s)")
                    with st.expander("View Errors"):
                        for error in errors:
                            st.text(error)
                
                # Clear state
                del st.session_state.pending_imports
                del st.session_state.show_import_confirmation
                st.session_state.show_batch_import = False
                
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state.pending_imports
                del st.session_state.show_import_confirmation
                st.session_state.show_batch_import = False
                st.rerun()
