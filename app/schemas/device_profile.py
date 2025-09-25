"""
Pydantic schemas for device profiles.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, AfterValidator

from app.validators.device_profile import validate_country_code, validate_custom_headers


class DeviceType(str, Enum):
    """Device type enumeration."""
    DESKTOP = "desktop"
    MOBILE = "mobile"


class CustomHeader(BaseModel):
    """Custom header schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., max_length=1000)
    secret: bool = Field(default=False, description="Whether this header contains secret data that should be encrypted")


class DeviceProfileBase(BaseModel):
    """Base device profile schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    device_type: DeviceType
    window_width: int = Field(..., ge=100, le=10000)
    window_height: int = Field(..., ge=100, le=10000)
    user_agent: str = Field(..., min_length=1, max_length=1000)
    country: Annotated[Optional[str], AfterValidator(validate_country_code)] = Field(None, min_length=2, max_length=2)
    custom_headers: Annotated[List[CustomHeader], AfterValidator(validate_custom_headers)] = Field(default_factory=list)
    extras: Dict = Field(default_factory=dict)
    
    
    @model_validator(mode='after')
    def validate_window_size_for_device_type(self):
        """Validate window size based on device type."""
        # Simple validation: mobile devices should not have ultra-wide viewports
        if self.device_type == DeviceType.MOBILE and (self.window_width > 2000 or self.window_height > 2000):
            raise ValueError("Mobile devices should not have ultra-wide viewports")
        return self


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
    country: Annotated[Optional[str], AfterValidator(validate_country_code)] = Field(None, min_length=2, max_length=2)
    custom_headers: Optional[List[CustomHeader]] = None
    extras: Optional[Dict] = None
    
    


class DeviceProfileResponse(DeviceProfileBase):
    """Schema for device profile responses."""
    
    id: UUID
    owner_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
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
    country: Annotated[Optional[str], AfterValidator(validate_country_code)] = Field(None, min_length=2, max_length=2)
    custom_headers: Optional[List[CustomHeader]] = None
    extras: Optional[Dict] = None
    
