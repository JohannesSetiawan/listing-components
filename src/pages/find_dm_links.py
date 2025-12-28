"""Find DM Links page - Extract form_data_ids from JSON and generate URLs"""

import streamlit as st
import json
import os

def extract_form_data_ids(obj, form_data_ids=None):
    """
    Recursively extract all form_data_id values from a nested JSON structure.
    
    Args:
        obj: The object to search (dict, list, or primitive)
        form_data_ids: Set to store unique form_data_id values
    
    Returns:
        Set of unique form_data_id values
    """
    if form_data_ids is None:
        form_data_ids = set()
    
    if isinstance(obj, dict):
        # Check if current dict has form_data_id key
        if 'form_data_id' in obj:
            value = obj['form_data_id']
            # Only add non-empty strings
            if value and isinstance(value, str) and value.strip():
                form_data_ids.add(value)
        
        # Recursively check all values in the dictionary
        for value in obj.values():
            extract_form_data_ids(value, form_data_ids)
    
    elif isinstance(obj, list):
        # Recursively check all items in the list
        for item in obj:
            extract_form_data_ids(item, form_data_ids)
    
    return form_data_ids


def load_id_to_tablegroup_mapping():
    """Load the indexed-data-managers.json mapping file"""
    json_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'indexed-data-managers.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def render_find_dm_links():
    """Render the Find DM Links page"""
    st.title("🔗 Find DM Links")
    st.markdown("**Extract form_data_id values from JSON and generate Data Manager URLs**")
    st.markdown("---")
    
    # Load the ID to tablegroup mapping
    id_to_tablegroup = load_id_to_tablegroup_mapping()
    
    # Initialize session state for clear button counter
    if 'dm_links_clear_counter' not in st.session_state:
        st.session_state.dm_links_clear_counter = 0
    
    # JSON input area
    st.subheader("📥 Input JSON")
    json_input = st.text_area(
        "Paste your JSON content here:",
        height=300,
        placeholder='{\n  "form_data_id": "example_id",\n  "nested": {\n    "form_data_id": "another_id"\n  }\n}',
        key=f"dm_links_text_area_{st.session_state.dm_links_clear_counter}"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        process_btn = st.button("🔍 Extract Links", type="primary")
    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.dm_links_clear_counter += 1
            st.rerun()
    
    if process_btn and json_input.strip():
        try:
            # Parse JSON input
            data = json.loads(json_input)
            
            # Extract form_data_ids
            form_data_ids = extract_form_data_ids(data)
            sorted_ids = sorted(form_data_ids)
            
            st.markdown("---")
            st.subheader("📤 Results")
            
            if not sorted_ids:
                st.warning("No form_data_id values found in the provided JSON.")
            else:
                st.success(f"Found **{len(sorted_ids)}** unique form_data_id values")
                
                # Separate found and not found IDs
                found_links = []
                not_found_ids = []
                
                for form_id in sorted_ids:
                    if form_id in id_to_tablegroup:
                        tablegroup_id = id_to_tablegroup[form_id]
                        url = f"https://studio-uat2.smart-cimb.com/#/form-data/table/{tablegroup_id}/{form_id}"
                        found_links.append((form_id, url))
                    else:
                        not_found_ids.append(form_id)
                
                # Display found links
                if found_links:
                    st.markdown("### ✅ Generated URLs")
                    
                    # Create copyable text of all URLs
                    all_urls = "\n".join([f"- {url}" for _, url in found_links])
                    
                    with st.expander("📋 Copy All URLs", expanded=True):
                        st.code(all_urls, language=None)
                    
                    # Display as clickable links
                    st.markdown("### 🔗 Clickable Links")
                    for form_id, url in found_links:
                        st.markdown(f"- [{form_id}]({url})")
                
                # Display not found IDs
                if not_found_ids:
                    st.markdown("---")
                    st.warning(f"⚠️ {len(not_found_ids)} form_data_id(s) not found in indexed-data-managers.json:")
                    for form_id in not_found_ids:
                        st.markdown(f"- `{form_id}`")
                        
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {str(e)}")
    elif process_btn:
        st.warning("Please paste some JSON content first.")
    
    # Help section
    st.markdown("---")
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Paste JSON**: Copy and paste your JSON content (e.g., component configuration) into the text area above.
        2. **Click Extract**: Click the "Extract Links" button to process the JSON.
        3. **View Results**: The tool will recursively search for all `form_data_id` values and generate corresponding Data Manager URLs.
        4. **Copy URLs**: Use the expandable section to copy all URLs at once, or click individual links to open them.
        
        **Note**: Only `form_data_id` values that exist in the `indexed-data-managers.json` mapping file will have URLs generated.
        """)
