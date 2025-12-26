"""Utility functions for the application"""

from src.config import VP_TYPES, EM_TYPES, DM_TYPES
from src.models.component import Category

def get_type_options(category):
    """Get type options based on category"""
    if category == Category.VP:
        return VP_TYPES
    elif category == Category.EM:
        return EM_TYPES
    elif category == Category.DM:
        return DM_TYPES
    return []
