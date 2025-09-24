"""
Device Profile CRUD tests.
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models.device_profile import DeviceProfile


class TestDeviceProfileCRUD:
    """Test device profile CRUD operations."""

    def test_create_device_profile_success(self, client, authenticated_headers, sample_device_profile_data):
        """Test creating a device profile with valid data."""
        response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["name"] == sample_device_profile_data["name"]
        assert data["device_type"] == sample_device_profile_data["device_type"]
        assert data["window_width"] == sample_device_profile_data["window_width"]
        assert data["window_height"] == sample_device_profile_data["window_height"]
        assert data["user_agent"] == sample_device_profile_data["user_agent"]
        assert data["country"] == sample_device_profile_data["country"]
        assert data["custom_headers"] == sample_device_profile_data["custom_headers"]
        assert data["extras"] == sample_device_profile_data["extras"]
        assert data["version"] == 1
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_device_profile_success(self, client, authenticated_headers, sample_device_profile_data, db_session, test_user):
        """Test retrieving an existing device profile."""
        # Create a profile first
        create_response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.json()["id"]
        
        # Get the profile
        response = client.get(
            f"/api/v1/device-profiles/{profile_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == profile_id
        assert data["name"] == sample_device_profile_data["name"]
        assert "ETag" in response.headers
        assert response.headers["ETag"] == 'W/"1"'

    def test_get_device_profile_not_found(self, client, authenticated_headers):
        """Test retrieving a non-existent device profile."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        
        response = client.get(
            f"/api/v1/device-profiles/{fake_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_device_profile_success(self, client, authenticated_headers, sample_device_profile_data, db_session, test_user):
        """Test updating an existing device profile."""
        # Create a profile first
        create_response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.json()["id"]
        etag = create_response.headers["ETag"]
        
        # Update the profile
        update_data = {
            "name": "Updated Profile Name",
            "window_width": 2560,
            "window_height": 1440
        }
        
        response = client.patch(
            f"/api/v1/device-profiles/{profile_id}",
            json=update_data,
            headers={**authenticated_headers, "If-Match": etag}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["window_width"] == update_data["window_width"]
        assert data["window_height"] == update_data["window_height"]
        assert data["version"] == 2  # Version should increment
        assert "ETag" in response.headers
        assert response.headers["ETag"] == 'W/"2"'

    def test_delete_device_profile_success(self, client, authenticated_headers, sample_device_profile_data, db_session, test_user):
        """Test soft deleting a device profile."""
        # Create a profile first
        create_response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.json()["id"]
        
        # Delete the profile
        response = client.delete(
            f"/api/v1/device-profiles/{profile_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify profile is soft deleted (not in list)
        list_response = client.get(
            "/api/v1/device-profiles",
            headers=authenticated_headers
        )
        assert list_response.status_code == status.HTTP_200_OK
        profiles = list_response.json()["items"]
        assert len(profiles) == 0

    def test_list_device_profiles_pagination(self, client, authenticated_headers, sample_device_profile_data, db_session, test_user):
        """Test paginated listing of device profiles."""
        import uuid
        # Create multiple profiles with unique names
        for i in range(3):
            profile_data = {
                "name": f"Profile {i+1} {uuid.uuid4().hex[:8]}",
                "device_type": "desktop",
                "window_width": 1920,
                "window_height": 1080,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "country": "us",
                "custom_headers": [{"name": "Accept-Language", "value": "en-US,en;q=0.9"}],
                "extras": {}
            }
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            assert response.status_code == status.HTTP_201_CREATED
        
        # List profiles
        response = client.get(
            "/api/v1/device-profiles",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        assert len(data["items"]) == 3
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["size"] == 50  # Default page size
        
        # Verify profile data
        for profile in data["items"]:
            assert "id" in profile
            assert "name" in profile
            assert "device_type" in profile
            assert "version" in profile

    def test_create_profile_duplicate_name(self, client, authenticated_headers, sample_device_profile_data, db_session, test_user):
        """Test creating a profile with duplicate name fails."""
        # Create first profile
        response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create second profile with same name
        response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]

    def test_update_profile_version_mismatch(self, client, authenticated_headers, sample_device_profile_data, db_session, test_user):
        """Test updating a profile with wrong version fails."""
        # Create a profile first
        create_response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.json()["id"]
        
        # Try to update with wrong version
        update_data = {"name": "Updated Name"}
        
        response = client.patch(
            f"/api/v1/device-profiles/{profile_id}",
            json=update_data,
            headers={**authenticated_headers, "If-Match": 'W/"999"'}  # Wrong version
        )
        
        assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
        assert "Version mismatch" in response.json()["detail"]

    def test_update_profile_missing_if_match(self, client, authenticated_headers, sample_device_profile_data, db_session, test_user):
        """Test updating a profile without If-Match header fails."""
        # Create a profile first
        create_response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.json()["id"]
        
        # Try to update without If-Match header
        update_data = {"name": "Updated Name"}
        
        response = client.patch(
            f"/api/v1/device-profiles/{profile_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_428_PRECONDITION_REQUIRED
        assert "If-Match header required" in response.json()["detail"]
