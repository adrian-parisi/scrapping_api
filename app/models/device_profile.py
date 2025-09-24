"""
Device profile database model.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, JSON, ForeignKey, Index, func, CheckConstraint
from sqlalchemy.types import Enum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship, declared_attr

from app.db import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin
from app.schemas.device_profile import DeviceType


class DeviceProfile(Base, TimestampMixin, SoftDeleteMixin):
    """Device profile configuration for web scraping requests."""
    
    __tablename__ = "profiles"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Owner scoping
    owner_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Profile details
    name = Column(Text, nullable=False)
    device_type = Column(Enum(DeviceType, name="device_type"), nullable=False)
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
    
    # Relationships
    owner = relationship("User", back_populates="device_profiles")
    
    # Unique constraint: (owner_id, lower(name)) for active profiles only
    @declared_attr.directive
    def __table_args__(cls):
        return (
        # Per-owner, case-insensitive unique name among ACTIVE (not soft-deleted) profiles
        Index(
            "ix_profiles_owner_name_active",
            "owner_id",
            func.lower(cls.name),
            unique=True,
            sqlite_where=cls.deleted_at.is_(None),
            postgresql_where=cls.deleted_at.is_(None),
        ),
        # Sane bounds for viewport
        CheckConstraint("window_width BETWEEN 100 AND 10000", name="ck_profiles_window_width_bounds"),
        CheckConstraint("window_height BETWEEN 100 AND 10000", name="ck_profiles_window_height_bounds"),
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<DeviceProfile(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
    
    def increment_version(self) -> None:
        """Increment the version number."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)