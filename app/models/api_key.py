"""
API key database model.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.db import Base


class APIKey(Base):
    """API key for ZenRows API authentication."""
    
    __tablename__ = "api_keys"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Owner scoping
    owner_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Hashed API key
    key_hash = Column(Text, nullable=False, unique=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="api_keys")
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<APIKey(id={self.id}, owner_id={self.owner_id})>"
    
