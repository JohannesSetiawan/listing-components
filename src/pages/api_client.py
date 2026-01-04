"""API Client page - Combined view with detail form on top and list below"""

import streamlit as st
import requests
import json
import xml.dom.minidom
import re
from src.utils.database import db
from datetime import datetime


def prettify_html(html_string):
    """
    Pretty format HTML with proper indentation.
    Uses a simple regex-based approach without external dependencies.
    """
    # Remove existing excessive whitespace
    html_string = re.sub(r'>\s+<', '><', html_string.strip())
    
    # Self-closing tags and void elements
    void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 
                     'link', 'meta', 'param', 'source', 'track', 'wbr'}
    
    result = []
    indent = 0
    indent_str = "  "
    
    # Split by tags while keeping the tags
    parts = re.split(r'(<[^>]+>)', html_string)
    
    for part in parts:
        if not part.strip():
            continue
            
        # Check if it's a tag
        if part.startswith('<'):
            tag_match = re.match(r'<(/?)(\w+)', part)
            if tag_match:
                is_closing = tag_match.group(1) == '/'
                tag_name = tag_match.group(2).lower()
                
                # Check for self-closing or void elements
                is_self_closing = part.endswith('/>') or tag_name in void_elements
                
                if is_closing:
                    indent = max(0, indent - 1)
                    result.append(indent_str * indent + part)
                elif is_self_closing:
                    result.append(indent_str * indent + part)
                else:
                    result.append(indent_str * indent + part)
                    indent += 1
            else:
                # Comments, doctypes, etc.
                result.append(indent_str * indent + part)
        else:
            # Text content
            text = part.strip()
            if text:
                result.append(indent_str * max(0, indent) + text)
    
    return '\n'.join(result)


def prettify_xml(xml_string):
    """
    Pretty format XML with proper indentation.
    Falls back to regex-based approach if minidom fails.
    """
    try:
        # First try xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_string.encode('utf-8'))
        pretty = dom.toprettyxml(indent="  ")
        # Remove extra blank lines that minidom adds
        lines = [line for line in pretty.split('\n') if line.strip()]
        return '\n'.join(lines)
    except Exception:
        # Fallback to simple regex-based formatting
        xml_string = re.sub(r'>\s+<', '><', xml_string.strip())
        
        result = []
        indent = 0
        indent_str = "  "
        
        parts = re.split(r'(<[^>]+>)', xml_string)
        
        for part in parts:
            if not part.strip():
                continue
                
            if part.startswith('</'):
                indent = max(0, indent - 1)
                result.append(indent_str * indent + part)
            elif part.startswith('<?') or part.startswith('<!'):
                result.append(indent_str * indent + part)
            elif part.startswith('<') and part.endswith('/>'):
                result.append(indent_str * indent + part)
            elif part.startswith('<'):
                result.append(indent_str * indent + part)
                indent += 1
            else:
                text = part.strip()
                if text:
                    result.append(indent_str * max(0, indent) + text)
        
        return '\n'.join(result)


def is_html_content(body, content_type):
    """
    Detect if the response body is HTML content.
    """
    # Check content type header
    if "text/html" in content_type or "application/xhtml" in content_type:
        return True
    
    # Check for HTML indicators in the body
    body_lower = body.strip().lower()
    html_indicators = [
        '<!doctype html',
        '<html',
        '<head',
        '<body',
        '<div',
        '<span',
        '<p>',
        '<h1',
        '<h2',
        '<h3',
        '<script',
        '<style',
        '<meta',
        '<link',
        '<title'
    ]
    
    return any(indicator in body_lower for indicator in html_indicators)


def render_api_client():
    """Render the combined API Client page with detail on top and list below"""
    st.title("📡 API Client")
    
    # Initialize session state
    if 'api_response' not in st.session_state:
        st.session_state.api_response = None
    if 'api_error' not in st.session_state:
        st.session_state.api_error = None
    if 'api_client_selected_request' not in st.session_state:
        st.session_state.api_client_selected_request = None
    
    # Load saved request if selected
    saved_request = None
    if st.session_state.api_client_selected_request:
        try:
            saved_request = db.get_api_request_by_uid(st.session_state.api_client_selected_request)
        except Exception as e:
            st.error(f"Error loading saved request: {str(e)}")
    
    # Header with current status
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        if saved_request:
            st.markdown(f"**Editing:** {saved_request.name}")
        else:
            st.markdown("**New Request**")
    
    with header_col2:
        if saved_request:
            if st.button("➕ New Request", type="secondary"):
                st.session_state.api_client_selected_request = None
                st.session_state.api_response = None
                st.session_state.api_error = None
                # Clear form data session state
                for key in ['api_params', 'api_headers', 'api_form_data', 
                           'params_request_uid', 'headers_request_uid', 'form_data_request_uid']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    st.markdown("---")
    
    # ==================== REQUEST DETAIL SECTION ====================
    render_request_detail(saved_request)
    
    # ==================== SAVED REQUESTS LIST SECTION ====================
    st.markdown("---")
    st.markdown("---")
    render_requests_list()


def render_request_detail(saved_request):
    """Render the request detail/form section"""
    
    # Request Configuration
    st.subheader("📥 Request Configuration")
    
    # Request name and description (for saving)
    with st.expander("💾 Request Details (for saving)", expanded=not saved_request):
        req_name = st.text_input(
            "Request Name",
            value=saved_request.name if saved_request else "",
            placeholder="My API Request",
            help="A name to identify this request"
        )
        
        req_description = st.text_area(
            "Description (optional)",
            value=saved_request.description if saved_request else "",
            placeholder="Describe what this request does...",
            height=80
        )
    
    # Method and URL
    method_col, url_col = st.columns([1, 4])
    
    with method_col:
        method = st.selectbox(
            "Method",
            options=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            index=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"].index(
                saved_request.method if saved_request else "GET"
            )
        )
    
    with url_col:
        url = st.text_input(
            "URL",
            value=saved_request.url if saved_request else "",
            placeholder="https://api.example.com/endpoint"
        )
    
    # Tabs for different configurations
    tab_params, tab_headers, tab_auth, tab_body = st.tabs([
        "📋 Params", "📝 Headers", "🔐 Auth", "📦 Body"
    ])
    
    # Query Parameters Tab
    with tab_params:
        st.markdown("**Query Parameters**")
        st.caption("These will be appended to the URL as ?key=value&key2=value2")
        
        # Load saved params
        saved_params = []
        if saved_request and saved_request.query_params:
            try:
                saved_params = json.loads(saved_request.query_params)
            except:
                saved_params = []
        
        # Initialize params in session state
        if 'api_params' not in st.session_state or st.session_state.get('params_request_uid') != (saved_request.uid if saved_request else None):
            st.session_state.api_params = saved_params if saved_params else [{"key": "", "value": "", "enabled": True}]
            st.session_state.params_request_uid = saved_request.uid if saved_request else None
        
        # Render params
        params_to_remove = []
        for i, param in enumerate(st.session_state.api_params):
            col1, col2, col3, col4 = st.columns([2, 2, 0.5, 0.5])
            
            with col1:
                st.session_state.api_params[i]["key"] = st.text_input(
                    "Key", value=param.get("key", ""), key=f"param_key_{i}",
                    label_visibility="collapsed", placeholder="Key"
                )
            with col2:
                st.session_state.api_params[i]["value"] = st.text_input(
                    "Value", value=param.get("value", ""), key=f"param_value_{i}",
                    label_visibility="collapsed", placeholder="Value"
                )
            with col3:
                st.session_state.api_params[i]["enabled"] = st.checkbox(
                    "Enable", value=param.get("enabled", True), key=f"param_enabled_{i}",
                    label_visibility="collapsed"
                )
            with col4:
                if st.button("🗑️", key=f"param_del_{i}"):
                    params_to_remove.append(i)
        
        # Remove params
        for i in reversed(params_to_remove):
            st.session_state.api_params.pop(i)
        if params_to_remove:
            st.rerun()
        
        if st.button("➕ Add Parameter"):
            st.session_state.api_params.append({"key": "", "value": "", "enabled": True})
            st.rerun()
    
    # Headers Tab
    with tab_headers:
        st.markdown("**Custom Headers**")
        
        # Load saved headers
        saved_headers = []
        if saved_request and saved_request.headers:
            try:
                saved_headers = json.loads(saved_request.headers)
            except:
                saved_headers = []
        
        # Initialize headers in session state
        if 'api_headers' not in st.session_state or st.session_state.get('headers_request_uid') != (saved_request.uid if saved_request else None):
            default_headers = saved_headers if saved_headers else [
                {"key": "Content-Type", "value": "application/json", "enabled": True}
            ]
            st.session_state.api_headers = default_headers
            st.session_state.headers_request_uid = saved_request.uid if saved_request else None
        
        # Render headers
        headers_to_remove = []
        for i, header in enumerate(st.session_state.api_headers):
            col1, col2, col3, col4 = st.columns([2, 2, 0.5, 0.5])
            
            with col1:
                st.session_state.api_headers[i]["key"] = st.text_input(
                    "Key", value=header.get("key", ""), key=f"header_key_{i}",
                    label_visibility="collapsed", placeholder="Header Name"
                )
            with col2:
                st.session_state.api_headers[i]["value"] = st.text_input(
                    "Value", value=header.get("value", ""), key=f"header_value_{i}",
                    label_visibility="collapsed", placeholder="Header Value"
                )
            with col3:
                st.session_state.api_headers[i]["enabled"] = st.checkbox(
                    "Enable", value=header.get("enabled", True), key=f"header_enabled_{i}",
                    label_visibility="collapsed"
                )
            with col4:
                if st.button("🗑️", key=f"header_del_{i}"):
                    headers_to_remove.append(i)
        
        # Remove headers
        for i in reversed(headers_to_remove):
            st.session_state.api_headers.pop(i)
        if headers_to_remove:
            st.rerun()
        
        if st.button("➕ Add Header"):
            st.session_state.api_headers.append({"key": "", "value": "", "enabled": True})
            st.rerun()
    
    # Auth Tab
    with tab_auth:
        st.markdown("**Authentication**")
        
        # Load saved auth
        saved_auth = {}
        if saved_request and saved_request.auth_config:
            try:
                saved_auth = json.loads(saved_request.auth_config)
            except:
                saved_auth = {}
        
        auth_type = st.selectbox(
            "Auth Type",
            options=["None", "Bearer Token", "Basic Auth", "API Key"],
            index=["None", "Bearer Token", "Basic Auth", "API Key"].index(
                saved_auth.get("type", "None")
            )
        )
        
        auth_config = {"type": auth_type}
        
        if auth_type == "Bearer Token":
            auth_config["token"] = st.text_input(
                "Token",
                value=saved_auth.get("token", ""),
                type="password",
                placeholder="Enter your bearer token"
            )
        
        elif auth_type == "Basic Auth":
            auth_col1, auth_col2 = st.columns(2)
            with auth_col1:
                auth_config["username"] = st.text_input(
                    "Username",
                    value=saved_auth.get("username", "")
                )
            with auth_col2:
                auth_config["password"] = st.text_input(
                    "Password",
                    value=saved_auth.get("password", ""),
                    type="password"
                )
        
        elif auth_type == "API Key":
            api_key_col1, api_key_col2 = st.columns(2)
            with api_key_col1:
                auth_config["key_name"] = st.text_input(
                    "Key Name",
                    value=saved_auth.get("key_name", "X-API-Key"),
                    placeholder="X-API-Key"
                )
            with api_key_col2:
                auth_config["key_value"] = st.text_input(
                    "Key Value",
                    value=saved_auth.get("key_value", ""),
                    type="password"
                )
            auth_config["add_to"] = st.radio(
                "Add to",
                options=["Header", "Query Params"],
                index=0 if saved_auth.get("add_to", "Header") == "Header" else 1,
                horizontal=True
            )
    
    # Body Tab
    with tab_body:
        st.markdown("**Request Body**")
        
        # Load saved body
        saved_body_type = "none"
        saved_body_content = ""
        if saved_request and saved_request.body:
            try:
                body_data = json.loads(saved_request.body)
                saved_body_type = body_data.get("type", "none")
                saved_body_content = body_data.get("content", "")
            except:
                pass
        
        body_type = st.radio(
            "Body Type",
            options=["none", "raw", "form-data", "x-www-form-urlencoded"],
            format_func=lambda x: {
                "none": "None",
                "raw": "Raw (JSON, XML, Text)",
                "form-data": "Form Data",
                "x-www-form-urlencoded": "x-www-form-urlencoded"
            }.get(x, x),
            horizontal=True,
            index=["none", "raw", "form-data", "x-www-form-urlencoded"].index(saved_body_type)
        )
        
        body_content = None
        
        if body_type == "raw":
            raw_type = st.selectbox(
                "Content Type",
                options=["JSON", "XML", "Text", "HTML"]
            )
            
            default_raw = saved_body_content if saved_body_content else ('{\n  \n}' if raw_type == "JSON" else "")
            
            body_content = st.text_area(
                "Body Content",
                value=default_raw,
                height=200,
                placeholder="Enter your request body here..."
            )
        
        elif body_type in ["form-data", "x-www-form-urlencoded"]:
            # Initialize form data
            if 'api_form_data' not in st.session_state or st.session_state.get('form_data_request_uid') != (saved_request.uid if saved_request else None):
                if saved_body_content and isinstance(saved_body_content, list):
                    st.session_state.api_form_data = saved_body_content
                else:
                    st.session_state.api_form_data = [{"key": "", "value": "", "enabled": True}]
                st.session_state.form_data_request_uid = saved_request.uid if saved_request else None
            
            form_to_remove = []
            for i, form_item in enumerate(st.session_state.api_form_data):
                col1, col2, col3, col4 = st.columns([2, 2, 0.5, 0.5])
                
                with col1:
                    st.session_state.api_form_data[i]["key"] = st.text_input(
                        "Key", value=form_item.get("key", ""), key=f"form_key_{i}",
                        label_visibility="collapsed", placeholder="Key"
                    )
                with col2:
                    st.session_state.api_form_data[i]["value"] = st.text_input(
                        "Value", value=form_item.get("value", ""), key=f"form_value_{i}",
                        label_visibility="collapsed", placeholder="Value"
                    )
                with col3:
                    st.session_state.api_form_data[i]["enabled"] = st.checkbox(
                        "Enable", value=form_item.get("enabled", True), key=f"form_enabled_{i}",
                        label_visibility="collapsed"
                    )
                with col4:
                    if st.button("🗑️", key=f"form_del_{i}"):
                        form_to_remove.append(i)
            
            for i in reversed(form_to_remove):
                st.session_state.api_form_data.pop(i)
            if form_to_remove:
                st.rerun()
            
            if st.button("➕ Add Field", key="add_form_field"):
                st.session_state.api_form_data.append({"key": "", "value": "", "enabled": True})
                st.rerun()
            
            body_content = st.session_state.api_form_data
    
    st.markdown("---")
    
    # Action buttons
    action_col1, action_col2, action_col3, action_col4 = st.columns([1, 1, 1, 2])
    
    with action_col1:
        send_btn = st.button("🚀 Send Request", type="primary")
    
    with action_col2:
        save_btn = st.button("💾 Save Request")
    
    with action_col3:
        if st.button("🗑️ Clear Response"):
            st.session_state.api_response = None
            st.session_state.api_error = None
            st.rerun()
    
    # Save request
    if save_btn:
        if not req_name.strip():
            st.error("Please enter a request name to save")
        elif not url.strip():
            st.error("Please enter a URL")
        else:
            try:
                # Build body data
                body_data = {"type": body_type, "content": body_content}
                
                request_data = {
                    "name": req_name.strip(),
                    "description": req_description.strip() if req_description else "",
                    "method": method,
                    "url": url.strip(),
                    "query_params": json.dumps(st.session_state.get('api_params', [])),
                    "headers": json.dumps(st.session_state.get('api_headers', [])),
                    "auth_config": json.dumps(auth_config),
                    "body": json.dumps(body_data)
                }
                
                if saved_request:
                    # Update existing
                    db.update_api_request(saved_request.uid, request_data)
                    st.success("Request updated successfully!")
                else:
                    # Create new
                    new_request = db.create_api_request(request_data)
                    st.session_state.api_client_selected_request = new_request.uid
                    st.success("Request saved successfully!")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error saving request: {str(e)}")
    
    # Send request
    if send_btn:
        if not url.strip():
            st.error("Please enter a URL")
        else:
            execute_request(
                method=method,
                url=url.strip(),
                params=st.session_state.get('api_params', []),
                headers=st.session_state.get('api_headers', []),
                auth_config=auth_config,
                body_type=body_type,
                body_content=body_content
            )
    
    # Display response
    render_response()


def render_requests_list():
    """Render the saved requests list section"""
    st.subheader("📋 Saved Requests")
    
    # Search and filter
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search by name, URL, or description...",
            label_visibility="collapsed",
            key="list_search"
        )
    
    with search_col2:
        method_filter = st.selectbox(
            "Filter by Method",
            options=["All", "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            label_visibility="collapsed",
            key="list_method_filter"
        )
    
    with search_col3:
        if st.button("🔄 Refresh List"):
            st.rerun()
    
    # Get saved requests from database
    try:
        method_to_filter = None if method_filter == "All" else method_filter
        requests_list, total = db.get_all_api_requests(
            search=search_query if search_query else None,
            method=method_to_filter
        )
        
        if not requests_list:
            st.info("No saved requests found. Fill out the form above and click 'Save Request' to create one.")
            return
        
        st.write(f"**Total:** {total} request(s)")
        
        # Display requests as cards
        for req in requests_list:
            render_request_card(req)
            
    except Exception as e:
        st.error(f"Error loading requests: {str(e)}")


def render_request_card(req):
    """Render a single request card"""
    method_colors = {
        "GET": "🟢",
        "POST": "🟡",
        "PUT": "🟠",
        "PATCH": "🟣",
        "DELETE": "🔴",
        "HEAD": "⚪",
        "OPTIONS": "🔵"
    }
    
    method_emoji = method_colors.get(req.method, "⚫")
    
    # Check if this is the currently selected request
    is_selected = st.session_state.get('api_client_selected_request') == req.uid
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            name_display = f"### {method_emoji} **{req.name}**"
            if is_selected:
                name_display += " ✏️"
            st.markdown(name_display)
            st.markdown(f"`{req.method}` | {req.url[:80]}{'...' if len(req.url) > 80 else ''}")
            if req.description:
                st.caption(req.description[:100] + ('...' if len(req.description) > 100 else ''))
        
        with col2:
            st.caption(f"Updated: {req.updated_at.strftime('%Y-%m-%d %H:%M') if req.updated_at else 'N/A'}")
        
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if is_selected:
                    st.button("✅ Selected", key=f"open_{req.uid}", disabled=True)
                else:
                    if st.button("📂 Open", key=f"open_{req.uid}"):
                        st.session_state.api_client_selected_request = req.uid
                        st.session_state.api_response = None
                        st.session_state.api_error = None
                        # Clear form data session state to reload from saved request
                        for key in ['api_params', 'api_headers', 'api_form_data', 
                                   'params_request_uid', 'headers_request_uid', 'form_data_request_uid']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
            
            with btn_col2:
                if st.button("🗑️", key=f"delete_{req.uid}"):
                    st.session_state.confirm_delete_request = req.uid
                    st.rerun()
        
        # Confirm delete dialog
        if st.session_state.get('confirm_delete_request') == req.uid:
            st.warning(f"Are you sure you want to delete '{req.name}'?")
            confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 3])
            
            with confirm_col1:
                if st.button("✅ Yes, Delete", key=f"confirm_del_{req.uid}"):
                    try:
                        # If deleting the currently selected request, clear selection
                        if st.session_state.get('api_client_selected_request') == req.uid:
                            st.session_state.api_client_selected_request = None
                            st.session_state.api_response = None
                            st.session_state.api_error = None
                        
                        db.delete_api_request(req.uid)
                        st.session_state.confirm_delete_request = None
                        st.success("Request deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting request: {str(e)}")
            
            with confirm_col2:
                if st.button("❌ Cancel", key=f"cancel_del_{req.uid}"):
                    st.session_state.confirm_delete_request = None
                    st.rerun()
        
        st.markdown("---")


def execute_request(method, url, params, headers, auth_config, body_type, body_content):
    """Execute the API request"""
    try:
        # Build query params
        query_params = {}
        for param in params:
            if param.get("enabled") and param.get("key"):
                query_params[param["key"]] = param["value"]
        
        # Build headers
        request_headers = {}
        for header in headers:
            if header.get("enabled") and header.get("key"):
                request_headers[header["key"]] = header["value"]
        
        # Add auth
        auth = None
        if auth_config.get("type") == "Bearer Token":
            token = auth_config.get("token", "")
            if token:
                request_headers["Authorization"] = f"Bearer {token}"
        
        elif auth_config.get("type") == "Basic Auth":
            username = auth_config.get("username", "")
            password = auth_config.get("password", "")
            if username:
                auth = (username, password)
        
        elif auth_config.get("type") == "API Key":
            key_name = auth_config.get("key_name", "")
            key_value = auth_config.get("key_value", "")
            if key_name and key_value:
                if auth_config.get("add_to") == "Header":
                    request_headers[key_name] = key_value
                else:
                    query_params[key_name] = key_value
        
        # Build body
        data = None
        json_body = None
        
        if body_type == "raw" and body_content:
            # Check if it's JSON
            try:
                json_body = json.loads(body_content)
            except:
                data = body_content
        
        elif body_type == "form-data" and body_content:
            data = {}
            for item in body_content:
                if item.get("enabled") and item.get("key"):
                    data[item["key"]] = item["value"]
        
        elif body_type == "x-www-form-urlencoded" and body_content:
            data = {}
            for item in body_content:
                if item.get("enabled") and item.get("key"):
                    data[item["key"]] = item["value"]
            # Update content type
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        # Make request
        with st.spinner(f"Sending {method} request..."):
            import time
            start_time = time.time()
            
            response = requests.request(
                method=method,
                url=url,
                params=query_params if query_params else None,
                headers=request_headers if request_headers else None,
                auth=auth,
                json=json_body,
                data=data if not json_body else None,
                timeout=60
            )
            
            elapsed_time = time.time() - start_time
            
            # Store response
            st.session_state.api_response = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
                "elapsed_time": round(elapsed_time * 1000, 2),  # ms
                "size": len(response.content)
            }
            st.session_state.api_error = None
            
    except requests.exceptions.Timeout:
        st.session_state.api_error = "Request timed out (60s). Please try again."
        st.session_state.api_response = None
    except requests.exceptions.ConnectionError as e:
        st.session_state.api_error = f"Connection error: {str(e)}"
        st.session_state.api_response = None
    except requests.exceptions.RequestException as e:
        st.session_state.api_error = f"Request failed: {str(e)}"
        st.session_state.api_response = None
    except Exception as e:
        st.session_state.api_error = f"Error: {str(e)}"
        st.session_state.api_response = None
    
    st.rerun()


def render_response():
    """Render the API response"""
    if st.session_state.api_error:
        st.error(st.session_state.api_error)
        return
    
    if not st.session_state.api_response:
        return
    
    st.markdown("---")
    st.subheader("📤 Response")
    
    response = st.session_state.api_response
    status_code = response["status_code"]
    
    # Status line with metadata
    status_col1, status_col2, status_col3 = st.columns([1, 1, 1])
    
    with status_col1:
        if 200 <= status_code < 300:
            st.success(f"Status: {status_code}")
        elif 300 <= status_code < 400:
            st.info(f"Status: {status_code}")
        elif 400 <= status_code < 500:
            st.warning(f"Status: {status_code}")
        else:
            st.error(f"Status: {status_code}")
    
    with status_col2:
        st.metric("Time", f"{response['elapsed_time']} ms")
    
    with status_col3:
        size_kb = response['size'] / 1024
        st.metric("Size", f"{size_kb:.2f} KB" if size_kb >= 1 else f"{response['size']} B")
    
    # Response tabs
    body_tab, headers_tab = st.tabs(["📄 Body", "📝 Headers"])
    
    with body_tab:
        content_type = response["headers"].get("Content-Type", "").lower()
        body = response["body"]
        
        # Detect content type for formatting
        is_json = "application/json" in content_type or body.strip().startswith(("{", "["))
        is_xml = ("xml" in content_type or 
                  body.strip().startswith("<?xml") or 
                  (body.strip().startswith("<") and not body.strip().startswith("<!DOCTYPE") and not is_html_content(body, content_type)))
        is_html = is_html_content(body, content_type)
        
        # View mode selector
        view_mode = st.radio(
            "View Mode",
            options=["Pretty", "Raw", "Preview"] if is_html else ["Pretty", "Raw"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if view_mode == "Pretty":
            if is_json:
                try:
                    parsed_json = json.loads(body)
                    st.json(parsed_json)
                except json.JSONDecodeError:
                    st.code(body, language="text")
            
            elif is_xml:
                try:
                    pretty_xml = prettify_xml(body)
                    st.code(pretty_xml, language="xml")
                except Exception:
                    st.code(body, language="xml")
            
            elif is_html:
                try:
                    pretty_html = prettify_html(body)
                    st.code(pretty_html, language="html")
                except Exception:
                    st.code(body, language="html")
            
            else:
                st.code(body, language="text")
        
        elif view_mode == "Preview" and is_html:
            # Render HTML preview in an iframe-like container
            st.markdown("**HTML Preview:**")
            st.components.v1.html(body, height=500, scrolling=True)
        
        else:
            st.code(body, language="text")
        
        # Copy button
        with st.expander("📋 Copy Response"):
            st.code(body, language="text")
    
    with headers_tab:
        st.markdown("**Response Headers**")
        headers_data = response["headers"]
        
        for key, value in headers_data.items():
            st.markdown(f"**{key}:** `{value}`")
