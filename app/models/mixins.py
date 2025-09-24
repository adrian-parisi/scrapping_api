"""
Database model mixins for common functionality.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime


class TimestampMixin:
    """Mixin for models that track creation and update timestamps."""
    
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SoftDeleteMixin:
    """Mixin for models that support soft deletion."""
    
    # Soft delete timestamp
    deleted_at = Column(DateTime, nullable=True)
    
    def is_active(self) -> bool:
        """Check if record is active (not soft deleted)."""
        return self.deleted_at is None
    
    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.deleted_at = datetime.now(timezone.utc)
        if hasattr(self, 'updated_at'):
            self.updated_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """Restore a soft deleted record."""
        self.deleted_at = None
        if hasattr(self, 'updated_at'):
            self.updated_at = datetime.now(timezone.utc)
