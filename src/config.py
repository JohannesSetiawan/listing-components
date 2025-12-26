"""Configuration module for database and environment settings"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get database URL from Streamlit secrets or environment variables"""
    db_url = None
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'DB_URL' in st.secrets:
            db_url = st.secrets['DB_URL']
    except:
        pass
    
    # Fall back to environment variable
    if not db_url:
        db_url = os.getenv('DB_URL', 'sqlite:///deploytrack.db')
    
    return db_url

# Type options for each category
VP_TYPES = ["API", "DJOB", "Function", "Workflow", "Integration"]
EM_TYPES = ["Single UI", "Multiple UI", "Dashboard", "Form", "Report"]
DM_TYPES = ["Schema", "Table", "View", "Stored Procedure", "ETL Pipeline"]
