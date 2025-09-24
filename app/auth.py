"""
API key authentication for ZenRows Device Profile API.
"""

import hashlib
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models.api_key import APIKey
from app.settings import settings

# HTTP Bearer security scheme
security = HTTPBearer()


def hash_api_key(api_key: str) -> str:
    """
    Hash API key with pepper using SHA-256.
    
    Args:
        api_key: Raw API key
        
    Returns:
        str: Hashed API key
    """
    return hashlib.sha256(f"{api_key}{settings.api_key_pepper}".encode()).hexdigest()


def get_current_owner_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UUID:
    """
    Get current owner ID from API key.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        UUID: Owner ID
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Hash the provided API key
    api_key_hash = hash_api_key(credentials.credentials)
    
    # Look up API key in database
    result = db.execute(select(APIKey).where(APIKey.key_hash == api_key_hash))
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key.owner_id
