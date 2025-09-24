"""
Device profile database model.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.db import Base


class DeviceType(str, Enum):
    """Device type enumeration."""
    DESKTOP = "desktop"
    MOBILE = "mobile"


class DeviceProfile(Base):
    """Device profile configuration for web scraping requests."""
    
    __tablename__ = "profiles"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Owner scoping
    owner_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
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
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="device_profiles")
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<DeviceProfile(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
    
    def is_active(self) -> bool:
        """Check if profile is active (not soft deleted)."""
        return self.deleted_at is None
    
    def soft_delete(self) -> None:
        """Soft delete the profile."""
        self.deleted_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def increment_version(self) -> None:
        """Increment the version number."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)
    
