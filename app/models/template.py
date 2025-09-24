"""
Template database model.
"""

from datetime import datetime
from typing import Dict
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db import Base


class Template(Base):
    """Template database model."""
    
    __tablename__ = "templates"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Template details
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Template data as full profile-like payload snapshot
    data = Column(JSON, nullable=False)
    
    # Template version (e.g., "Chrome 120", "iOS 17")
    version = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<Template(id={self.id}, name={self.name}, version={self.version})>"
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
