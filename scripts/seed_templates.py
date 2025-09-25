#!/usr/bin/env python3
"""
Database seeding script for device profile templates.

This script creates predefined templates that users can use to create device profiles.
It should be run after the database is created and before the API is used.

Usage:
    python scripts/seed_templates.py
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.template import Template


def seed_templates():
    """Seed the database with predefined templates."""
    db: Session = SessionLocal()
    
    try:
        # Check if templates already exist
        existing_templates = db.query(Template).count()
        if existing_templates > 0:
            print(f"Templates already exist ({existing_templates} found). Skipping seeding.")
            return
        
        # Define predefined templates
        templates = [
            {
                "name": "Chrome Desktop (Latest)",
                "description": "Latest Chrome browser on Windows desktop",
                "version": "Chrome 120",
                "data": {
                    "name": "Chrome Desktop Profile",
                    "device_type": "desktop",
                    "window_width": 1920,
                    "window_height": 1080,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "country": "us",
                    "custom_headers": [
                        {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
                        {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                        {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
                    ],
                    "extras": {
                        "browser": "chrome",
                        "os": "windows",
                        "version": "120.0.0.0"
                    }
                }
            },
            {
                "name": "Safari Mobile (iOS 17)",
                "description": "Safari browser on iPhone with iOS 17",
                "version": "iOS 17",
                "data": {
                    "name": "Safari Mobile Profile",
                    "device_type": "mobile",
                    "window_width": 375,
                    "window_height": 667,
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "country": "us",
                    "custom_headers": [
                        {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
                        {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                        {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
                    ],
                    "extras": {
                        "browser": "safari",
                        "os": "ios",
                        "version": "17.0",
                        "device": "iphone"
                    }
                }
            },
            {
                "name": "Firefox Desktop (Latest)",
                "description": "Latest Firefox browser on Linux desktop",
                "version": "Firefox 121",
                "data": {
                    "name": "Firefox Desktop Profile",
                    "device_type": "desktop",
                    "window_width": 1920,
                    "window_height": 1080,
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
                    "country": "us",
                    "custom_headers": [
                        {"name": "Accept-Language", "value": "en-US,en;q=0.5"},
                        {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                        {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}
                    ],
                    "extras": {
                        "browser": "firefox",
                        "os": "linux",
                        "version": "121.0"
                    }
                }
            },
            {
                "name": "Chrome Mobile (Android 14)",
                "description": "Chrome browser on Android 14 device",
                "version": "Android 14",
                "data": {
                    "name": "Chrome Mobile Profile",
                    "device_type": "mobile",
                    "window_width": 412,
                    "window_height": 915,
                    "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                    "country": "us",
                    "custom_headers": [
                        {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
                        {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                        {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
                    ],
                    "extras": {
                        "browser": "chrome",
                        "os": "android",
                        "version": "14",
                        "device": "samsung_galaxy"
                    }
                }
            },
            {
                "name": "Edge Desktop (Latest)",
                "description": "Latest Microsoft Edge browser on Windows desktop",
                "version": "Edge 120",
                "data": {
                    "name": "Edge Desktop Profile",
                    "device_type": "desktop",
                    "window_width": 1920,
                    "window_height": 1080,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                    "country": "us",
                    "custom_headers": [
                        {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
                        {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                        {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
                    ],
                    "extras": {
                        "browser": "edge",
                        "os": "windows",
                        "version": "120.0.0.0"
                    }
                }
            }
        ]
        
        # Create and insert templates
        for template_data in templates:
            template = Template(**template_data)
            db.add(template)
        
        # Commit all templates
        db.commit()
        
        print(f"✅ Successfully seeded {len(templates)} templates:")
        for template in templates:
            print(f"  - {template['name']} ({template['version']})")
        
    except Exception as e:
        print(f"❌ Error seeding templates: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_templates()
