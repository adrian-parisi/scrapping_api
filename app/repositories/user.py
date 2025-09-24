"""
User repository for data access operations.
"""

import secrets
import hashlib
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.api_key import APIKey
from app.settings import settings


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(self, email: str) -> User:
        """
        Create a new user.
        
        Args:
            email: User email address
            
        Returns:
            User: Created user
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        existing_user = self.get_by_email(email)
        if existing_user:
            raise ValueError(f"User with email '{email}' already exists")
        
        user = User(
            email=email
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email address
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_api_key(self, user_id: UUID) -> tuple[APIKey, str]:
        """
        Create a new API key for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            tuple[APIKey, str]: API key object and raw key
            
        Raises:
            ValueError: If user not found
        """
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID '{user_id}' not found")
        
        # Generate raw API key
        raw_key = secrets.token_urlsafe(32)
        
        # Hash the key with pepper
        key_hash = hashlib.sha256(f"{raw_key}{settings.api_key_pepper}".encode()).hexdigest()
        
        # Create API key record
        api_key = APIKey(
            owner_id=user_id,
            key_hash=key_hash
        )
        
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key, raw_key
    
    def get_api_keys(self, user_id: UUID) -> List[APIKey]:
        """
        Get all API keys for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[APIKey]: List of API keys
        """
        return self.db.query(APIKey).filter(APIKey.owner_id == user_id).all()
    
    def get_or_create_user(self, email: str) -> User:
        """
        Get existing user or create new one.
        
        Args:
            email: User email address
            
        Returns:
            User: Existing or newly created user
        """
        user = self.get_by_email(email)
        if user:
            return user
        
        return self.create(email)
