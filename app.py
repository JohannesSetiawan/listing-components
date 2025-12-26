import streamlit as st
import requests
from datetime import datetime

# Configure the page
st.set_page_config(
    page_title="Listing Helper",
    page_icon="🏠",
    layout="wide"
)

# API Functions
def hello_world_api():
    """Simple Hello World API endpoint simulation"""
    return {
        "message": "Hello World!",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success"
    }

# Main App
def main():
    # Header
    st.title("🏠 Listing Helper")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", ["Home", "API Test"])
        st.markdown("---")
        st.info("A simple Streamlit app with API functionality")
    
    # Home Page
    if page == "Home":
        st.header("Welcome to Listing Helper!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("About")
            st.write("""
            This is a basic Streamlit application with:
            - Interactive frontend
            - API endpoint simulation
            - Ready for Streamlit Cloud deployment
            """)
        
        with col2:
            st.subheader("Quick Stats")
            st.metric("API Status", "Active", "100%")
            st.metric("Version", "1.0.0")
        
        # Input example
        st.markdown("---")
        st.subheader("Try it out")
        user_name = st.text_input("Enter your name:")
        if user_name:
            st.success(f"Hello, {user_name}! 👋")
    
    # API Test Page
    elif page == "API Test":
        st.header("API Test")
        st.write("Test the Hello World API endpoint")
        
        if st.button("Call API", type="primary"):
            with st.spinner("Calling API..."):
                response = hello_world_api()
                
                st.success("API Response:")
                st.json(response)
                
                # Display in a nicer format
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", response["status"])
                with col2:
                    st.metric("Message", response["message"])
                with col3:
                    st.metric("Timestamp", response["timestamp"])

if __name__ == "__main__":
    main()
