"""Database operations and connection management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.models.component import Base, Component, Category, ChangeType, ApiRequest
from src.config import get_database_url

class Database:
    def __init__(self):
        db_url = get_database_url()
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def create_component(self, component_data):
        session = self.get_session()
        try:
            component = Component(**component_data)
            session.add(component)
            session.commit()
            session.refresh(component)
            return component
        finally:
            session.close()
    
    def get_all_components(self, category=None, type_filter=None, search=None, limit=50, offset=0):
        session = self.get_session()
        try:
            query = session.query(Component)
            
            if category:
                query = query.filter(Component.category == category)
            
            if type_filter:
                query = query.filter(Component.type == type_filter)
            
            if search:
                query = query.filter(
                    (Component.name.contains(search)) | 
                    (Component.description.contains(search)) |
                    (Component.component_id.contains(search))
                )
            
            total = query.count()
            components = query.order_by(Component.created_at.desc()).limit(limit).offset(offset).all()
            
            return components, total
        finally:
            session.close()
    
    def get_component_by_uid(self, uid):
        session = self.get_session()
        try:
            return session.query(Component).filter(Component.uid == uid).first()
        finally:
            session.close()
    
    def update_component(self, uid, update_data):
        session = self.get_session()
        try:
            component = session.query(Component).filter(Component.uid == uid).first()
            if component:
                for key, value in update_data.items():
                    setattr(component, key, value)
                component.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(component)
                return component
            return None
        finally:
            session.close()
    
    def delete_component(self, uid):
        session = self.get_session()
        try:
            component = session.query(Component).filter(Component.uid == uid).first()
            if component:
                session.delete(component)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_types_by_category(self, category):
        session = self.get_session()
        try:
            types = session.query(Component.type).filter(
                Component.category == category
            ).distinct().all()
            return [t[0] for t in types]
        finally:
            session.close()
    
    # API Request methods
    def create_api_request(self, request_data):
        """Create a new API request"""
        session = self.get_session()
        try:
            api_request = ApiRequest(**request_data)
            session.add(api_request)
            session.commit()
            session.refresh(api_request)
            return api_request
        finally:
            session.close()
    
    def get_all_api_requests(self, search=None, method=None, limit=50, offset=0):
        """Get all API requests with optional filters"""
        session = self.get_session()
        try:
            query = session.query(ApiRequest)
            
            if method:
                query = query.filter(ApiRequest.method == method)
            
            if search:
                query = query.filter(
                    (ApiRequest.name.contains(search)) | 
                    (ApiRequest.description.contains(search)) |
                    (ApiRequest.url.contains(search))
                )
            
            total = query.count()
            requests = query.order_by(ApiRequest.updated_at.desc()).limit(limit).offset(offset).all()
            
            return requests, total
        finally:
            session.close()
    
    def get_api_request_by_uid(self, uid):
        """Get a single API request by UID"""
        session = self.get_session()
        try:
            return session.query(ApiRequest).filter(ApiRequest.uid == uid).first()
        finally:
            session.close()
    
    def update_api_request(self, uid, update_data):
        """Update an existing API request"""
        session = self.get_session()
        try:
            api_request = session.query(ApiRequest).filter(ApiRequest.uid == uid).first()
            if api_request:
                for key, value in update_data.items():
                    setattr(api_request, key, value)
                api_request.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(api_request)
                return api_request
            return None
        finally:
            session.close()
    
    def delete_api_request(self, uid):
        """Delete an API request"""
        session = self.get_session()
        try:
            api_request = session.query(ApiRequest).filter(ApiRequest.uid == uid).first()
            if api_request:
                session.delete(api_request)
                session.commit()
                return True
            return False
        finally:
            session.close()

# Initialize database
db = Database()
