"""
Template repository for data access operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.template import Template
from app.schemas.device_profile import DeviceProfileCreateFromTemplate
from app.schemas.template import CreateProfileFromTemplateRequest


class TemplateRepository:
    """Repository for template operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def list(self) -> List[Template]:
        """
        List all templates.
        
        Returns:
            List[Template]: All templates
        """
        return self.db.query(Template).order_by(Template.name).all()
    
    def get_by_id(self, template_id: UUID) -> Optional[Template]:
        """
        Get template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Optional[Template]: Template if found, None otherwise
        """
        return self.db.query(Template).filter(Template.id == template_id).first()
    
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
                profile_data["custom_headers"] = [header.model_dump() for header in value]
            else:
                profile_data[field] = value
        
        return profile_data
