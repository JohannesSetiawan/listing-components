import streamlit as st
from datetime import datetime
import pandas as pd
from database import db, Category, ChangeType

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

# Type options for each category
VP_TYPES = ["API", "DJOB", "Function", "Workflow", "Integration"]
EM_TYPES = ["Single UI", "Multiple UI", "Dashboard", "Form", "Report"]
DM_TYPES = ["Schema", "Table", "View", "Stored Procedure", "ETL Pipeline"]

def get_type_options(category):
    """Get type options based on category"""
    if category == Category.VP:
        return VP_TYPES
    elif category == Category.EM:
        return EM_TYPES
    elif category == Category.DM:
        return DM_TYPES
    return []

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
    
    # Add new component button
    if st.button("➕ Add New Component", type="primary"):
        st.session_state.edit_mode = "new"
        st.rerun()
    
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

# Main App
def main():
    # Sidebar
    with st.sidebar:
        st.title("📋 Navigation")
        
        page = st.radio(
            "Go to",
            [
                "🏠 Home",
                "📊 Master List",
                "⚙️ Visual Programming",
                "🎨 Experience Manager",
                "💾 Data Manager"
            ]
        )
        
        st.markdown("---")
        
        st.info("**DeployTrack Low-Code**\n\nTrack and manage deployment components across your low-code ecosystem.")
        
        # API Test
        st.markdown("---")
        if st.button("🧪 Test API"):
            response = {
                "message": "Hello World!",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success",
                "total_components": db.get_all_components(limit=1)[1]
            }
            st.json(response)
    
    # Main content
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

if __name__ == "__main__":
    main()
