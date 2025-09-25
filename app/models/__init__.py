# Database models for ZenRows Device Profile API

# Import Base from db module
from app.db import Base

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.api_key import APIKey
from app.models.device_profile import DeviceProfile
from app.models.template import Template

__all__ = [
    "Base",
    "User",
    "APIKey", 
    "DeviceProfile",
    "Template",
]
