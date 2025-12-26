from sqlalchemy import create_engine, Column, String, DateTime, Enum
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

# Initialize database
db = Database()
