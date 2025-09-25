#!/usr/bin/env python3
"""
Command-line script to create a user and generate an API key.

This script is for technical interview purposes only and is NOT suitable for production use.
It creates users and API keys without any authentication or security measures.

Usage:
    python scripts/create_user.py <email>

Examples:
    python scripts/create_user.py user@example.com
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.repositories.user import UserRepository

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # noqa: F401, F403


def main():
    """Main function to create user and generate API key."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_user.py <email>")
        print("Example: python scripts/create_user.py user@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    # Validate email format (basic check)
    if '@' not in email or '.' not in email.split('@')[-1]:
        print(f"Error: Invalid email format: {email}")
        sys.exit(1)
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Create user repository
        user_repo = UserRepository(db)
        
        # Get or create user
        try:
            user = user_repo.get_or_create_user(email)
            print(f"User found/created: {user.email}")
        except ValueError as e:
            print(f"Error creating user: {e}")
            sys.exit(1)
        
        # Generate API key
        try:
            api_key, raw_key = user_repo.create_api_key(user.id)
            print(f"\n✅ API Key generated successfully!")
            print(f"User ID: {user.id}")
            print(f"API Key: {raw_key}")
            print(f"\n⚠️  IMPORTANT: Save this API key now - it won't be shown again!")
            print(f"⚠️  This script is for technical interview purposes only - NOT for production!")
            
        except ValueError as e:
            print(f"Error generating API key: {e}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
