"""
API key database model.
"""

from datetime import datetime
from typing import Dict
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db import Base


class APIKey(Base):
    """API key database model."""
    
    __tablename__ = "api_keys"
    
    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Owner scoping
    owner_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    
    # Hashed API key
    key_hash = Column(Text, nullable=False, unique=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<APIKey(id={self.id}, owner_id={self.owner_id})>"
    
    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self.last_used_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "owner_id": str(self.owner_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }
