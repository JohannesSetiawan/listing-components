"""Database models and enums"""

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import enum

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
    type = Column(String, nullable=False)
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
