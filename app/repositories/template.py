"""
Template repository for data access operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, Query
from sqlalchemy import select

from app.models.template import Template
from app.schemas.device_profile import DeviceProfileCreateFromTemplate
from app.schemas.template import CreateProfileFromTemplateRequest


class TemplateRepository:
    """Repository for template operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_query(self):
        """
        Get base query for templates.
        
        Returns:
            Query: SQLAlchemy query object for fastapi-pagination
        """
        return self.db.query(Template).order_by(Template.name)
    
    def list(self) -> List[Template]:
        """
        List all templates.
        
        Returns:
            List[Template]: All templates
        """
        result = self.db.execute(select(Template).order_by(Template.name))
        return list(result.scalars().all())
    
    def get_by_id(self, template_id: UUID) -> Optional[Template]:
        """
        Get template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Optional[Template]: Template if found, None otherwise
        """
        result = self.db.execute(
            select(Template).where(Template.id == template_id)
        )
        return result.scalar_one_or_none()
    
    def create_profile_from_template(
        self, 
        owner_id: UUID, 
        template_id: UUID, 
        overrides: CreateProfileFromTemplateRequest
    ) -> Optional[dict]:
        """
        Create a profile from template data with optional overrides.
        
        Args:
            owner_id: Owner ID
            template_id: Template ID
            overrides: Override data for the profile
            
        Returns:
            Optional[dict]: Profile data if template found, None otherwise
        """
        template = self.get_by_id(template_id)
        if not template:
            return None
        
        # Start with template data
        profile_data = template.data.copy()
        
        # Apply overrides
        override_dict = overrides.model_dump(exclude_unset=True)
        for field, value in override_dict.items():
            if field == "custom_headers" and value is not None:
                # Handle both Pydantic objects and dicts
                if hasattr(value[0], 'model_dump'):
                    profile_data["custom_headers"] = [header.model_dump() for header in value]
                else:
                    profile_data["custom_headers"] = value
            else:
                profile_data[field] = value
        
        return profile_data