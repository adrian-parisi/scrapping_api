"""
Template database model.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db import Base
from app.models.mixins import TimestampMixin


class Template(Base, TimestampMixin):
    """Predefined device profile templates."""
    
    __tablename__ = "templates"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Template details
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=False, default="")
    
    # Template data as full profile-like payload snapshot
    data = Column(JSON, nullable=False)
    
    # Template version (e.g., "Chrome 120", "iOS 17")
    version = Column(String(50), nullable=False, default="")
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<Template(id={self.id}, name={self.name}, version={self.version})>"
    