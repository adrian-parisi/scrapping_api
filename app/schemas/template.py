"""
Pydantic schemas for templates.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.device_profile import DeviceProfileCreateFromTemplate


class TemplateResponse(BaseModel):
    """Schema for template responses."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    data: Dict
    version: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class TemplateList(BaseModel):
    """Schema for paginated template list responses."""
    
    items: List[TemplateResponse]
    limit: int
    offset: int
    total: int
    count: int


class CreateProfileFromTemplateRequest(DeviceProfileCreateFromTemplate):
    """Schema for creating a profile from template request."""
    pass