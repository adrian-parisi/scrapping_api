"""
Pydantic schemas for device profiles.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.device_profile import DeviceType


class CustomHeader(BaseModel):
    """Custom header schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., max_length=1000)


class DeviceProfileBase(BaseModel):
    """Base device profile schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    device_type: DeviceType
    window_width: int = Field(..., ge=100, le=10000)
    window_height: int = Field(..., ge=100, le=10000)
    user_agent: str = Field(..., min_length=1, max_length=1000)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    custom_headers: List[CustomHeader] = Field(default_factory=list)
    extras: Dict = Field(default_factory=dict)
    
    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Validate country code."""
        if v is not None:
            if not v.isalpha():
                raise ValueError('Country code must contain only letters')
            if not v.islower():
                raise ValueError('Country code must be lowercase')
        return v
    
    @field_validator('custom_headers')
    @classmethod
    def validate_custom_headers(cls, v):
        """Validate custom headers."""
        if v:
            # Check for forbidden headers
            forbidden_headers = {
                "host", "content-length", "connection", "transfer-encoding",
                "keep-alive", "upgrade", "trailer"
            }
            for header in v:
                if header.name.lower() in forbidden_headers:
                    raise ValueError(f"Forbidden header: {header.name}")
        return v
    
    @field_validator('window_width', 'window_height')
    @classmethod
    def validate_window_size(cls, v, info):
        """Validate window size based on device type."""
        if info.data.get('device_type') == DeviceType.MOBILE:
            if v > 2000:
                raise ValueError('Mobile devices should not have ultra-wide viewports')
        return v


class DeviceProfileCreate(DeviceProfileBase):
    """Schema for creating a device profile."""
    pass


class DeviceProfileUpdate(BaseModel):
    """Schema for updating a device profile."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    device_type: Optional[DeviceType] = None
    window_width: Optional[int] = Field(None, ge=100, le=10000)
    window_height: Optional[int] = Field(None, ge=100, le=10000)
    user_agent: Optional[str] = Field(None, min_length=1, max_length=1000)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    custom_headers: Optional[List[CustomHeader]] = None
    extras: Optional[Dict] = None
    
    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Validate country code."""
        if v is not None:
            if not v.isalpha():
                raise ValueError('Country code must contain only letters')
            if not v.islower():
                raise ValueError('Country code must be lowercase')
        return v
    
    @field_validator('custom_headers')
    @classmethod
    def validate_custom_headers(cls, v):
        """Validate custom headers."""
        if v:
            # Check for forbidden headers
            forbidden_headers = {
                "host", "content-length", "connection", "transfer-encoding",
                "keep-alive", "upgrade", "trailer"
            }
            for header in v:
                if header.name.lower() in forbidden_headers:
                    raise ValueError(f"Forbidden header: {header.name}")
        return v


class DeviceProfileResponse(DeviceProfileBase):
    """Schema for device profile responses."""
    
    id: UUID
    owner_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    }


class DeviceProfileList(BaseModel):
    """Schema for paginated device profile list responses."""
    
    items: List[DeviceProfileResponse]
    limit: int
    offset: int
    total: int
    count: int


class DeviceProfileCreateFromTemplate(BaseModel):
    """Schema for creating a device profile from template."""
    
    name: str = Field(..., min_length=1, max_length=255)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    custom_headers: Optional[List[CustomHeader]] = None
    extras: Optional[Dict] = None
    
    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Validate country code."""
        if v is not None:
            if not v.isalpha():
                raise ValueError('Country code must contain only letters')
            if not v.islower():
                raise ValueError('Country code must be lowercase')
        return v
