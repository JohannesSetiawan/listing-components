"""Audit Trail page - Make POST requests to audit trail API"""

import streamlit as st
import requests
import json


def render_audit_trail():
    """Render the Audit Trail page"""
    st.title("📜 Audit Trail")
    st.markdown("**Query audit trail records from the API**")
    st.markdown("---")
    
    # Initialize session state for storing results
    if 'audit_trail_response' not in st.session_state:
        st.session_state.audit_trail_response = None
    if 'audit_trail_error' not in st.session_state:
        st.session_state.audit_trail_error = None
    
    # Input section
    st.subheader("📥 API Configuration")
    
    # API URL input
    api_url = st.text_input(
        "Audit Trail API URL",
        placeholder="https://<api>/v1/nocode/record/audit_trail",
        help="Enter the full URL for the audit trail endpoint"
    )
    
    # Authorization token input
    auth_token = st.text_input(
        "Authorization Token (JWT Bearer)",
        type="password",
        placeholder="Enter your JWT token",
        help="This will be used as Bearer token in the Authorization header. Get the token from the STUDIO not the app."
    )
    
    st.markdown("---")
    
    # Toggle between form input and custom JSON
    use_custom_body = st.toggle(
        "Use Custom Request Body",
        value=False,
        help="Enable to provide a custom JSON request body instead of using the form fields"
    )
    
    # Initialize variables
    form_data_id = ""
    record_id = ""
    page_num = 1
    limit = 500
    sort_order = ("Descending (newest first)", -1)
    custom_json_input = ""
    
    if use_custom_body:
        # Custom JSON input mode
        st.subheader("📝 Custom Request Body")
        
        default_body = '''{
    "form_data_id": "your_form_data_id",
    "page": 1,
    "limit": 500,
    "sort": {
        "timestamp": -1
    },
    "filter": {
        "record_id": "your_record_id"
    }
}'''
        
        custom_json_input = st.text_area(
            "Request Body (JSON)",
            value=default_body,
            height=250,
            help="Enter your custom JSON request body"
        )
    else:
        # Form input mode
        st.subheader("📋 Query Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            form_data_id = st.text_input(
                "Form Data ID",
                placeholder="Enter form_data_id",
                help="The form_data_id to query"
            )
        
        with col2:
            record_id = st.text_input(
                "Record ID",
                placeholder="Enter record_id",
                help="The record_id to filter by"
            )
        
        # Advanced options (collapsible)
        with st.expander("⚙️ Advanced Options"):
            adv_col1, adv_col2 = st.columns(2)
            with adv_col1:
                page_num = st.number_input("Page", min_value=1, value=1, help="Page number for pagination")
            with adv_col2:
                limit = st.number_input("Limit", min_value=1, max_value=1000, value=500, help="Number of records per page")
            
            sort_order = st.selectbox(
                "Sort Order (by timestamp)",
                options=[("Descending (newest first)", -1), ("Ascending (oldest first)", 1)],
                format_func=lambda x: x[0]
            )
    
    st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        submit_btn = st.button("🚀 Fetch Audit Trail", type="primary")
    
    with col2:
        if st.button("🗑️ Clear Results"):
            st.session_state.audit_trail_response = None
            st.session_state.audit_trail_error = None
            st.rerun()
    
    # Process request
    if submit_btn:
        # Validation
        if not api_url.strip():
            st.error("Please enter the API URL")
            return
        
        if not auth_token.strip():
            st.error("Please enter the Authorization Token")
            return
        
        if use_custom_body:
            # Parse custom JSON
            try:
                request_body = json.loads(custom_json_input)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON in request body: {str(e)}")
                return
        else:
            # Validate form fields
            if not form_data_id.strip():
                st.error("Please enter the Form Data ID")
                return
            
            if not record_id.strip():
                st.error("Please enter the Record ID")
                return
            
            # Build request body from form
            request_body = {
                "form_data_id": form_data_id.strip(),
                "page": page_num,
                "limit": limit,
                "sort": {
                    "timestamp": sort_order[1]
                },
                "filter": {
                    "record_id": record_id.strip()
                }
            }
        
        # Build headers
        headers = {
            "Authorization": f"Bearer {auth_token.strip()}",
            "Content-Type": "application/json"
        }
        
        # Make request
        with st.spinner("Fetching audit trail..."):
            try:
                response = requests.post(
                    api_url.strip(),
                    headers=headers,
                    json=request_body,
                    timeout=30
                )
                
                # Store response in session state
                st.session_state.audit_trail_error = None
                
                try:
                    st.session_state.audit_trail_response = {
                        "status_code": response.status_code,
                        "data": response.json()
                    }
                except json.JSONDecodeError:
                    st.session_state.audit_trail_response = {
                        "status_code": response.status_code,
                        "data": response.text
                    }
                    
            except requests.exceptions.Timeout:
                st.session_state.audit_trail_error = "Request timed out. Please try again."
                st.session_state.audit_trail_response = None
            except requests.exceptions.ConnectionError:
                st.session_state.audit_trail_error = "Connection error. Please check the URL and try again."
                st.session_state.audit_trail_response = None
            except requests.exceptions.RequestException as e:
                st.session_state.audit_trail_error = f"Request failed: {str(e)}"
                st.session_state.audit_trail_response = None
        
        st.rerun()
    
    # Display results
    if st.session_state.audit_trail_error:
        st.error(st.session_state.audit_trail_error)
    
    if st.session_state.audit_trail_response:
        st.markdown("---")
        st.subheader("📤 Response")
        
        response_data = st.session_state.audit_trail_response
        status_code = response_data["status_code"]
        
        # Display status code with appropriate color
        if 200 <= status_code < 300:
            st.success(f"Status Code: {status_code}")
        elif 400 <= status_code < 500:
            st.warning(f"Status Code: {status_code}")
        else:
            st.error(f"Status Code: {status_code}")
        
        # Display response data
        st.subheader("📄 Response Body")
        
        data = response_data["data"]
        
        if isinstance(data, dict) or isinstance(data, list):
            # Pretty print JSON
            st.json(data)
            
            # Also provide copyable text version
            with st.expander("📋 Copy as Text"):
                st.code(json.dumps(data, indent=2, ensure_ascii=False), language="json")
        else:
            # Plain text response
            st.code(data)
