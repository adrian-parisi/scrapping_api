"""
Device profile database model.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.db import Base


class DeviceType(str, Enum):
    """Device type enumeration."""
    DESKTOP = "desktop"
    MOBILE = "mobile"


class DeviceProfile(Base):
    """Device profile database model."""
    
    __tablename__ = "profiles"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Owner scoping
    owner_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    
    # Profile details
    name = Column(Text, nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    window_width = Column(Integer, nullable=False)
    window_height = Column(Integer, nullable=False)
    user_agent = Column(Text, nullable=False)
    country = Column(String(2), nullable=True)
    
    # Custom headers as array of {name, value} objects
    custom_headers = Column(JSON, nullable=False, default=list)
    
    # Additional data
    extras = Column(JSON, nullable=False, default=dict)
    
    # Versioning for ETag/If-Match
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<DeviceProfile(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
    
    def is_active(self) -> bool:
        """Check if profile is active (not soft deleted)."""
        return self.deleted_at is None
    
    def soft_delete(self) -> None:
        """Soft delete the profile."""
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def increment_version(self) -> None:
        """Increment the version number."""
        self.version += 1
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "owner_id": str(self.owner_id),
            "name": self.name,
            "device_type": self.device_type.value,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "user_agent": self.user_agent,
            "country": self.country,
            "custom_headers": self.custom_headers,
            "extras": self.extras,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
