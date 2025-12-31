from sqlalchemy import create_engine, Column, String, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import enum
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class ChangeType(enum.Enum):
    NEW = "New"
    UPDATED = "Updated"

class Category(enum.Enum):
    VP = "Visual Programming"
    EM = "Experience Manager"
    DM = "Data Manager"


class ApiRequest(Base):
    """Model for storing saved API requests (like Postman collections)"""
    __tablename__ = 'api_requests'
    
    uid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, default="")
    method = Column(String, nullable=False, default="GET")  # GET, POST, PUT, PATCH, DELETE, etc.
    url = Column(String, nullable=False)
    query_params = Column(Text, default="[]")  # JSON string of [{key, value, enabled}]
    headers = Column(Text, default="[]")  # JSON string of [{key, value, enabled}]
    auth_config = Column(Text, default="{}")  # JSON string of auth configuration
    body = Column(Text, default="")  # JSON string of {type, content}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'description': self.description,
            'method': self.method,
            'url': self.url,
            'query_params': self.query_params,
            'headers': self.headers,
            'auth_config': self.auth_config,
            'body': self.body,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class Component(Base):
    __tablename__ = 'components'
    
    uid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    component_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    url_link = Column(String, nullable=False)
    change_type = Column(Enum(ChangeType), nullable=False)
    description = Column(String, default="")
    category = Column(Enum(Category), nullable=False)
    type = Column(String, nullable=False)  # API, DJOB, Function, Single UI, Multiple UI, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uid': self.uid,
            'component_id': self.component_id,
            'name': self.name,
            'url_link': self.url_link,
            'change_type': self.change_type.value if isinstance(self.change_type, ChangeType) else self.change_type,
            'description': self.description,
            'category': self.category.value if isinstance(self.category, Category) else self.category,
            'type': self.type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Database:
    def __init__(self):
        # For Streamlit Cloud, check secrets first, then .env
        db_url = None
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'DB_URL' in st.secrets:
                db_url = st.secrets['DB_URL']
        except:
            pass
        
        if not db_url:
            db_url = os.getenv('DB_URL', 'sqlite:///deploytrack.db')
        
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
