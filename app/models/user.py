"""
User database model.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    """User account for API authentication."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User details
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Account status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    device_profiles = relationship("DeviceProfile", back_populates="owner", lazy="select")
    api_keys = relationship("APIKey", back_populates="owner", lazy="select")
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<User(id={self.id}, email={self.email})>"
    
