"""
Template API tests.
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.template import Template
from app.models.user import User
from app.models.api_key import APIKey
from app.auth import hash_api_key


class TestTemplateAPI:
    """Test template API functionality."""

    def test_list_templates_success(self, client, test_templates):
        """Test listing templates returns seeded items."""
        response = client.get("/api/v1/templates")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        
        # Should have templates
        templates = data["items"]
        assert isinstance(templates, list)
        assert len(templates) == 3  # We created 3 templates in the fixture
        
        # Verify structure
        template = templates[0]
        assert "id" in template
        assert "name" in template
        assert "description" in template
        assert "version" in template
        assert "data" in template

    def test_get_template_success(self, client, test_template):
        """Test getting a specific template by ID."""
        response = client.get(f"/api/v1/templates/{test_template.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(test_template.id)
        assert data["name"] == "Chrome Desktop"
        assert data["description"] == "Latest Chrome on Windows"
        assert data["version"] == "Chrome 120"
        assert data["data"]["device_type"] == "desktop"

    def test_get_template_not_found(self, client):
        """Test getting a non-existent template returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/templates/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Template not found"

    def test_create_profile_from_template_success(self, client, test_template, test_api_key):
        """Test creating a profile from a template."""
        _, raw_key = test_api_key
        
        # Test creating profile from template
        overrides = {
            "name": "My Custom Profile",
            "country": "gb"
        }
        
        response = client.post(
            f"/api/v1/templates/{test_template.id}/create-profile",
            json=overrides,
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify profile was created with template data + overrides
        assert data["name"] == "My Custom Profile"  # Override applied
        assert data["device_type"] == "desktop"  # From template
        assert data["window_width"] == 1920  # From template
        assert data["window_height"] == 1080  # From template
        assert data["country"] == "gb"  # Override applied
        assert data["user_agent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"  # From template
        assert len(data["custom_headers"]) == 1  # From template
        assert data["custom_headers"][0]["name"] == "Accept-Language"
        assert data["extras"]["browser"] == "chrome"  # From template
        
        # Verify Location header
        assert "Location" in response.headers
        assert f"/api/v1/device-profiles/{data['id']}" in response.headers["Location"]

    def test_create_profile_from_template_with_full_overrides(self, client, test_template, test_api_key):
        """Test creating a profile from template with full overrides."""
        _, raw_key = test_api_key
        
        # Test creating profile with supported overrides
        overrides = {
            "name": "Fully Custom Profile",
            "country": "fr",
            "custom_headers": [
                {"name": "Accept-Language", "value": "fr-FR,fr;q=0.9"},
                {"name": "X-Custom-Header", "value": "custom-value"}
            ],
            "extras": {"browser": "safari", "os": "ios"}
        }
        
        response = client.post(
            f"/api/v1/templates/{test_template.id}/create-profile",
            json=overrides,
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify all overrides were applied
        assert data["name"] == "Fully Custom Profile"
        assert data["country"] == "fr"
        assert len(data["custom_headers"]) == 2
        assert data["custom_headers"][0]["name"] == "Accept-Language"
        assert data["custom_headers"][0]["value"] == "fr-FR,fr;q=0.9"
        assert data["custom_headers"][1]["name"] == "X-Custom-Header"
        assert data["custom_headers"][1]["value"] == "custom-value"
        assert data["extras"]["browser"] == "safari"
        assert data["extras"]["os"] == "ios"
        
        # Verify template data is preserved for non-override fields
        assert data["device_type"] == "desktop"  # From template
        assert data["window_width"] == 1920  # From template
        assert data["window_height"] == 1080  # From template
        assert data["user_agent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"  # From template

    def test_create_profile_from_template_not_found(self, client, test_api_key):
        """Test creating profile from non-existent template returns 404."""
        _, raw_key = test_api_key
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        overrides = {"name": "Test Profile"}
        
        response = client.post(
            f"/api/v1/templates/{fake_id}/create-profile",
            json=overrides,
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Template not found"

    def test_create_profile_from_template_duplicate_name(self, client, test_template, test_api_key, db_session):
        """Test creating profile from template with duplicate name returns 409."""
        _, raw_key = test_api_key
        
        # Create a profile with the same name first
        from app.repositories.device_profile import DeviceProfileRepository
        from app.schemas.device_profile import DeviceProfileCreate
        
        profile_repo = DeviceProfileRepository(db_session)
        existing_profile = DeviceProfileCreate(
            name="Chrome Desktop Profile",  # Same name as template
            device_type="desktop",
            window_width=1920,
            window_height=1080,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            country="us",
            custom_headers=[],
            extras={}
        )
        profile_repo.create(test_api_key[0].owner_id, existing_profile)
        
        # Try to create another profile with the same name from template
        overrides = {"name": "Chrome Desktop Profile"}
        
        response = client.post(
            f"/api/v1/templates/{test_template.id}/create-profile",
            json=overrides,
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "Profile with name 'Chrome Desktop Profile' already exists" in data["detail"]

    def test_create_profile_from_template_requires_authentication(self, client, test_template):
        """Test that creating profile from template requires authentication."""
        overrides = {"name": "Test Profile"}
        
        response = client.post(
            f"/api/v1/templates/{test_template.id}/create-profile",
            json=overrides
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "API key required"
