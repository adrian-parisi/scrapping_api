"""
Device profile repository for data access operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, Query

from app.models.device_profile import DeviceProfile
from app.schemas.device_profile import DeviceProfileCreate, DeviceProfileUpdate


class DeviceProfileRepository:
    """Repository for device profile operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_query(self, owner_id: UUID) -> Query:
        """
        Get base query for device profiles filtered by owner.
        
        Args:
            owner_id: Owner ID to filter by
            
        Returns:
            Query: SQLAlchemy query object for fastapi-pagination
        """
        return self.db.query(DeviceProfile).filter(
            and_(
                DeviceProfile.owner_id == owner_id,
                DeviceProfile.deleted_at.is_(None)  # Only active profiles
            )
        ).order_by(DeviceProfile.created_at.desc())
    
    def create(self, owner_id: UUID, profile_data: DeviceProfileCreate) -> DeviceProfile:
        """
        Create a new device profile.
        
        Args:
            owner_id: Owner ID
            profile_data: Profile creation data
            
        Returns:
            DeviceProfile: Created profile
        """
        profile = DeviceProfile(
            owner_id=owner_id,
            name=profile_data.name,
            device_type=profile_data.device_type,
            window_width=profile_data.window_width,
            window_height=profile_data.window_height,
            user_agent=profile_data.user_agent,
            country=profile_data.country,
            custom_headers=[header.model_dump() for header in profile_data.custom_headers],
            extras=profile_data.extras
        )
        
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        
        return profile
    
    def get_by_id(self, owner_id: UUID, profile_id: UUID) -> Optional[DeviceProfile]:
        """
        Get device profile by ID (owner-scoped).
        
        Args:
            owner_id: Owner ID
            profile_id: Profile ID
            
        Returns:
            Optional[DeviceProfile]: Profile if found, None otherwise
        """
        result = self.db.execute(
            select(DeviceProfile).where(
                and_(
                    DeviceProfile.id == profile_id,
                    DeviceProfile.owner_id == owner_id,
                    DeviceProfile.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    def list(self, owner_id: UUID, limit: int, offset: int) -> tuple[List[DeviceProfile], int]:
        """
        List device profiles for owner (paginated).
        
        Args:
            owner_id: Owner ID
            limit: Number of items to return
            offset: Number of items to skip
            
        Returns:
            tuple[List[DeviceProfile], int]: Profiles and total count
        """
        base_query = select(DeviceProfile).where(
            and_(
                DeviceProfile.owner_id == owner_id,
                DeviceProfile.deleted_at.is_(None)
            )
        )
        
        # Get total count
        count_result = self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total_count = count_result.scalar()
        
        # Get paginated results
        profiles_result = self.db.execute(
            base_query.order_by(DeviceProfile.updated_at.desc()).offset(offset).limit(limit)
        )
        profiles = profiles_result.scalars().all()
        
        return list(profiles), total_count
    
    def update(self, owner_id: UUID, profile_id: UUID, update_data: DeviceProfileUpdate, version: int) -> Optional[DeviceProfile]:
        """
        Update device profile (with version check).
        
        Args:
            owner_id: Owner ID
            profile_id: Profile ID
            update_data: Update data
            version: Expected version for ETag check
            
        Returns:
            Optional[DeviceProfile]: Updated profile if found and version matches
        """
        profile = self.get_by_id(owner_id, profile_id)
        if not profile:
            return None
        
        # Check version for ETag/If-Match
        if profile.version != version:
            return None
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if field == "custom_headers" and value is not None:
                setattr(profile, field, [header.model_dump() for header in value])
            else:
                setattr(profile, field, value)
        
        # Increment version
        profile.increment_version()
        
        self.db.commit()
        self.db.refresh(profile)
        
        return profile
    
    def soft_delete(self, owner_id: UUID, profile_id: UUID) -> bool:
        """
        Soft delete device profile.
        
        Args:
            owner_id: Owner ID
            profile_id: Profile ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        profile = self.get_by_id(owner_id, profile_id)
        if not profile:
            return False
        
        profile.soft_delete()
        self.db.commit()
        
        return True
    
    def check_name_exists(self, owner_id: UUID, name: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if profile name exists for owner.
        
        Args:
            owner_id: Owner ID
            name: Profile name
            exclude_id: Profile ID to exclude from check
            
        Returns:
            bool: True if name exists, False otherwise
        """
        base_conditions = and_(
            DeviceProfile.owner_id == owner_id,
            DeviceProfile.name == name,
            DeviceProfile.deleted_at.is_(None)
        )
        
        if exclude_id:
            base_conditions = and_(base_conditions, DeviceProfile.id != exclude_id)
        
        result = self.db.execute(
            select(DeviceProfile).where(base_conditions)
        )
        
        return result.scalar_one_or_none() is not None
