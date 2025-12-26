"""
Database Initialization Script
Run this script to set up the database with sample data
"""

from src.models.component import Category, ChangeType
from src.utils.database import db

def init_database():
    """Initialize database with sample components"""
    
    print("🚀 Initializing DeployTrack Database...")
    
    # Sample Visual Programming components
    vp_samples = [
        {
            'component_id': 'VP-001',
            'name': 'Customer Authentication API',
            'url_link': 'https://lowcode.example.com/vp/auth-api',
            'type': 'API',
            'change_type': ChangeType.NEW,
            'description': 'New REST API for customer authentication with OAuth2 support',
            'category': Category.VP
        },
        {
            'component_id': 'VP-002',
            'name': 'Daily Sales Report DJOB',
            'url_link': 'https://lowcode.example.com/vp/sales-djob',
            'type': 'DJOB',
            'change_type': ChangeType.UPDATED,
            'description': 'Updated to include new metrics for Q4 reporting',
            'category': Category.VP
        },
        {
            'component_id': 'VP-003',
            'name': 'Email Notification Function',
            'url_link': 'https://lowcode.example.com/vp/email-func',
            'type': 'Function',
            'change_type': ChangeType.NEW,
            'description': 'Serverless function for sending transactional emails',
            'category': Category.VP
        }
    ]
    
    # Sample Experience Manager components
    em_samples = [
        {
            'component_id': 'EM-001',
            'name': 'Customer Dashboard',
            'url_link': 'https://lowcode.example.com/em/customer-dash',
            'type': 'Single UI',
            'change_type': ChangeType.UPDATED,
            'description': 'Updated dashboard with new KPI widgets and real-time data',
            'category': Category.EM
        },
        {
            'component_id': 'EM-002',
            'name': 'Admin Portal',
            'url_link': 'https://lowcode.example.com/em/admin-portal',
            'type': 'Multiple UI',
            'change_type': ChangeType.NEW,
            'description': 'Complete admin portal with user management and analytics',
            'category': Category.EM
        },
        {
            'component_id': 'EM-003',
            'name': 'Order Entry Form',
            'url_link': 'https://lowcode.example.com/em/order-form',
            'type': 'Form',
            'change_type': ChangeType.UPDATED,
            'description': 'Added validation for international shipping addresses',
            'category': Category.EM
        }
    ]
    
    # Sample Data Manager components
    dm_samples = [
        {
            'component_id': 'DM-001',
            'name': 'Customer Database Schema',
            'url_link': 'https://lowcode.example.com/dm/customer-schema',
            'type': 'Schema',
            'change_type': ChangeType.UPDATED,
            'description': 'Added new fields for GDPR compliance and data retention',
            'category': Category.DM
        },
        {
            'component_id': 'DM-002',
            'name': 'Sales Analytics View',
            'url_link': 'https://lowcode.example.com/dm/sales-view',
            'type': 'View',
            'change_type': ChangeType.NEW,
            'description': 'Materialized view for faster sales reporting queries',
            'category': Category.DM
        },
        {
            'component_id': 'DM-003',
            'name': 'Data Migration Pipeline',
            'url_link': 'https://lowcode.example.com/dm/migration-etl',
            'type': 'ETL Pipeline',
            'change_type': ChangeType.NEW,
            'description': 'ETL pipeline for migrating legacy customer data',
            'category': Category.DM
        }
    ]
    
    # Insert all sample data
    all_samples = vp_samples + em_samples + dm_samples
    
    for sample in all_samples:
        try:
            db.create_component(sample)
            print(f"✅ Created: {sample['name']}")
        except Exception as e:
            print(f"❌ Error creating {sample['name']}: {str(e)}")
    
    print(f"\n🎉 Database initialized with {len(all_samples)} sample components!")
    print("\nRun 'streamlit run app.py' to start the application.")

if __name__ == "__main__":
    init_database()
