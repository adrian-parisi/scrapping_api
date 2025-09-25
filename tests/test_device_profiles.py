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
        
        # Verify Location header
        assert "Location" in response.headers
        assert f"/api/v1/device-profiles/{data['id']}" in response.headers["Location"]

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

    def test_authentication_required_on_all_endpoints(self, client, test_api_key, sample_device_profile_data, db_session, test_user):
        """Test that authentication is required on all device profile endpoints."""
        from app.models.device_profile import DeviceProfile
        from app.schemas.device_profile import DeviceType
        
        _, raw_key = test_api_key
        headers = {"Authorization": f"Bearer {raw_key}"}
        
        # Create a profile first
        create_response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.json()["id"]
        
        # Test GET /device-profiles (list) without authentication
        response = client.get("/api/v1/device-profiles")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test GET /device-profiles/{id} without authentication
        response = client.get(f"/api/v1/device-profiles/{profile_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test PATCH /device-profiles/{id} without authentication
        response = client.patch(
            f"/api/v1/device-profiles/{profile_id}",
            json={"name": "Updated Profile"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test DELETE /device-profiles/{id} without authentication
        response = client.delete(f"/api/v1/device-profiles/{profile_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_access_other_users_profile(self, client, db_session, test_user, sample_device_profile_data, authenticated_headers):
        """Test that users cannot access other users' profiles (404, not 403)."""
        from app.models.user import User
        from app.models.api_key import APIKey
        import hashlib
        from app.settings import settings
        
        # Create another user
        other_user = User(email="other@example.com")
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        # Create API key for other user
        raw_key = "other-user-key-12345"
        key_hash = hashlib.sha256(f"{raw_key}{settings.api_key_pepper}".encode()).hexdigest()
        other_api_key = APIKey(owner_id=other_user.id, key_hash=key_hash)
        db_session.add(other_api_key)
        db_session.commit()
        
        # Create profile for test_user using authenticated headers
        create_response = client.post(
            "/api/v1/device-profiles",
            json=sample_device_profile_data,
            headers=authenticated_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.json()["id"]
        
        # Try to access with other user's credentials
        response = client.get(
            f"/api/v1/device-profiles/{profile_id}",
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        
        # Should return 404 (not 403) for other users' resources
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_country_validation(self, client, authenticated_headers, sample_device_profile_data):
        """Test country code validation using pycountry library."""
        import uuid
        
        # Test valid country codes
        valid_countries = ["us", "gb", "fr", "de", "ca", "au", "jp"]
        
        for i, country in enumerate(valid_countries):
            profile_data = sample_device_profile_data.copy()
            profile_data["country"] = country
            profile_data["name"] = f"Test Profile {country.upper()} {i}"  # Unique name
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["country"] == country
        
        # Test invalid country codes (must be 2 characters due to max_length=2)
        invalid_countries = ["xx", "zz", "12", "ab"]
        
        for i, country in enumerate(invalid_countries):
            profile_data = sample_device_profile_data.copy()
            profile_data["country"] = country
            profile_data["name"] = f"Invalid Profile {i}"  # Unique name
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            error_data = response.json()
            assert "errors" in error_data
            assert isinstance(error_data["errors"], list)
            assert len(error_data["errors"]) > 0
            # Check that the error is related to country validation
            country_errors = [err for err in error_data["errors"] if "country" in str(err.get("loc", []))]
            assert len(country_errors) > 0

    def test_window_size_validation(self, client, authenticated_headers, sample_device_profile_data):
        """Test window size validation (100-10000 range and mobile restrictions)."""
        # Test valid window sizes
        valid_sizes = [
            (100, 100),      # Minimum
            (1920, 1080),    # Common desktop
            (375, 667),      # Common mobile
            (10000, 10000)   # Maximum
        ]
        
        for i, (width, height) in enumerate(valid_sizes):
            profile_data = sample_device_profile_data.copy()
            profile_data["window_width"] = width
            profile_data["window_height"] = height
            profile_data["name"] = f"Valid Size {i}"
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["window_width"] == width
            assert response.json()["window_height"] == height
        
        # Test invalid window sizes (too small)
        invalid_sizes = [
            (99, 100, ["window_width"]),       # Width too small
            (100, 99, ["window_height"]),      # Height too small
            (50, 50, ["window_width", "window_height"]),  # Both too small
        ]
        
        for i, (width, height, expected_invalid_fields) in enumerate(invalid_sizes):
            profile_data = sample_device_profile_data.copy()
            profile_data["window_width"] = width
            profile_data["window_height"] = height
            profile_data["name"] = f"Invalid Small {i}"
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            error_data = response.json()
            assert "errors" in error_data
            assert isinstance(error_data["errors"], list)
            assert len(error_data["errors"]) > 0
            
            # Check that the expected fields have validation errors
            error_fields = [str(err.get("loc", [])) for err in error_data["errors"]]
            for expected_field in expected_invalid_fields:
                assert any(expected_field in field for field in error_fields), \
                    f"Expected {expected_field} to have validation error, but errors were: {error_fields}"
        
        # Test invalid window sizes (too large)
        invalid_large_sizes = [
            (10001, 1000, ["window_width"]),   # Width too large
            (1000, 10001, ["window_height"]),  # Height too large
            (20000, 20000, ["window_width", "window_height"]),  # Both too large
        ]
        
        for i, (width, height, expected_invalid_fields) in enumerate(invalid_large_sizes):
            profile_data = sample_device_profile_data.copy()
            profile_data["window_width"] = width
            profile_data["window_height"] = height
            profile_data["name"] = f"Invalid Large {i}"
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            error_data = response.json()
            assert "errors" in error_data
            assert isinstance(error_data["errors"], list)
            assert len(error_data["errors"]) > 0
            
            # Check that the expected fields have validation errors
            error_fields = [str(err.get("loc", [])) for err in error_data["errors"]]
            for expected_field in expected_invalid_fields:
                assert any(expected_field in field for field in error_fields), \
                    f"Expected {expected_field} to have validation error, but errors were: {error_fields}"
        
        # Test mobile ultra-wide restriction
        mobile_ultra_wide = {
            "name": "Mobile Ultra Wide",
            "device_type": "mobile",
            "window_width": 3000,  # Too wide for mobile
            "window_height": 2000,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "country": "us",
            "custom_headers": [],
            "extras": {}
        }
        
        response = client.post(
            "/api/v1/device-profiles",
            json=mobile_ultra_wide,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        error_data = response.json()
        assert "errors" in error_data
        assert isinstance(error_data["errors"], list)
        assert len(error_data["errors"]) > 0
        
        # Check that the error is related to window width validation for mobile devices
        error_fields = [str(err.get("loc", [])) for err in error_data["errors"]]
        # The mobile ultra-wide validation should trigger a validation error
        # We expect either window_width or a general validation error
        has_window_error = any("window_width" in field for field in error_fields)
        has_validation_error = any("__root__" in field or "body" in field for field in error_fields)
        assert has_window_error or has_validation_error, \
            f"Expected window_width or validation error for mobile ultra-wide, but errors were: {error_fields}"
        
        # Additional test: Verify specific error types and constraint information
        for error in error_data["errors"]:
            error_type = error.get("type", "")
            error_msg = error.get("msg", "")
            error_input = error.get("input")
            error_ctx = error.get("ctx", {})
            
            # Check that we have meaningful error information
            assert error_type, "Error should have a type"
            assert error_msg, "Error should have a message"
            assert error_input is not None, "Error should include the input value"
            
            # For range validation errors, check constraint information
            if "greater_than_equal" in error_type:
                assert "ge" in error_ctx, "Range validation should include constraint information"
                assert error_ctx["ge"] == 100, "Minimum window size should be 100"
            elif "less_than_equal" in error_type:
                assert "le" in error_ctx, "Range validation should include constraint information"
                assert error_ctx["le"] == 10000, "Maximum window size should be 10000"

    def test_custom_headers_validation(self, client, authenticated_headers, sample_device_profile_data):
        """Test custom headers validation (forbidden headers and format)."""
        # Test valid custom headers
        valid_headers = [
            {"name": "X-Custom-Header", "value": "test-value"},
            {"name": "User-Agent-Override", "value": "Custom Agent"},
            {"name": "X-API-Key", "value": "secret-key"},
            {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
        ]
        
        profile_data = sample_device_profile_data.copy()
        profile_data["custom_headers"] = valid_headers
        profile_data["name"] = "Valid Headers Profile"
        
        response = client.post(
            "/api/v1/device-profiles",
            json=profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()["custom_headers"]) == 4
        
        # Test forbidden hop-by-hop headers
        forbidden_hop_by_hop = [
            {"name": "Connection", "value": "close"},
            {"name": "Keep-Alive", "value": "timeout=5"},
            {"name": "Transfer-Encoding", "value": "chunked"},
            {"name": "Upgrade", "value": "websocket"},
        ]
        
        for i, header in enumerate(forbidden_hop_by_hop):
            profile_data = sample_device_profile_data.copy()
            profile_data["custom_headers"] = [header]
            profile_data["name"] = f"Forbidden Hop {i}"
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            error_data = response.json()
            assert "errors" in error_data
            assert isinstance(error_data["errors"], list)
            assert len(error_data["errors"]) > 0
            # Check that the error is related to custom headers validation
            header_errors = [err for err in error_data["errors"] if "custom_headers" in str(err.get("loc", []))]
            assert len(header_errors) > 0
        
        # Test forbidden controlled headers
        forbidden_controlled = [
            {"name": "Host", "value": "malicious.com"},
            {"name": "Content-Length", "value": "100"},
            {"name": "Content-Type", "value": "application/json"},
            {"name": "Content-Encoding", "value": "gzip"},
        ]
        
        for i, header in enumerate(forbidden_controlled):
            profile_data = sample_device_profile_data.copy()
            profile_data["custom_headers"] = [header]
            profile_data["name"] = f"Forbidden Controlled {i}"
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            error_data = response.json()
            assert "errors" in error_data
            assert isinstance(error_data["errors"], list)
            assert len(error_data["errors"]) > 0
            # Check that the error is related to custom headers validation
            header_errors = [err for err in error_data["errors"] if "custom_headers" in str(err.get("loc", []))]
            assert len(header_errors) > 0
        
        # Test forbidden security headers
        forbidden_security = [
            {"name": "Authorization", "value": "Bearer token"},
            {"name": "Cookie", "value": "session=abc123"},
            {"name": "Set-Cookie", "value": "session=abc123"},
            {"name": "WWW-Authenticate", "value": "Basic"},
        ]
        
        for i, header in enumerate(forbidden_security):
            profile_data = sample_device_profile_data.copy()
            profile_data["custom_headers"] = [header]
            profile_data["name"] = f"Forbidden Security {i}"
            
            response = client.post(
                "/api/v1/device-profiles",
                json=profile_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            error_data = response.json()
            assert "errors" in error_data
            assert isinstance(error_data["errors"], list)
            assert len(error_data["errors"]) > 0
            # Check that the error is related to custom headers validation
            header_errors = [err for err in error_data["errors"] if "custom_headers" in str(err.get("loc", []))]
            assert len(header_errors) > 0
        
        # Test case sensitivity (should be case-insensitive)
        profile_data = sample_device_profile_data.copy()
        profile_data["custom_headers"] = [{"name": "CONNECTION", "value": "close"}]
        profile_data["name"] = "Case Insensitive Test"
        
        response = client.post(
            "/api/v1/device-profiles",
            json=profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        error_data = response.json()
        assert "errors" in error_data
        assert isinstance(error_data["errors"], list)
        assert len(error_data["errors"]) > 0
        # Check that the error is related to custom headers validation
        header_errors = [err for err in error_data["errors"] if "custom_headers" in str(err.get("loc", []))]
        assert len(header_errors) > 0
        
        # Test empty header name (Pydantic field validation catches this first)
        profile_data = sample_device_profile_data.copy()
        profile_data["custom_headers"] = [{"name": "", "value": "test"}]
        profile_data["name"] = "Empty Header Name"
        
        response = client.post(
            "/api/v1/device-profiles",
            json=profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        error_data = response.json()
        assert "errors" in error_data
        assert isinstance(error_data["errors"], list)
        assert len(error_data["errors"]) > 0
        # Check that the error is related to custom headers validation
        header_errors = [err for err in error_data["errors"] if "custom_headers" in str(err.get("loc", []))]
        assert len(header_errors) > 0
        
        # Test whitespace-only header name (our custom validator catches this)
        profile_data = sample_device_profile_data.copy()
        profile_data["custom_headers"] = [{"name": "   ", "value": "test"}]
        profile_data["name"] = "Whitespace Header Name"
        
        response = client.post(
            "/api/v1/device-profiles",
            json=profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        error_data = response.json()
        assert "errors" in error_data
        assert isinstance(error_data["errors"], list)
        assert len(error_data["errors"]) > 0
        # Check that the error is related to custom headers validation
        header_errors = [err for err in error_data["errors"] if "custom_headers" in str(err.get("loc", []))]
        assert len(header_errors) > 0

    def test_custom_headers_preserve_order_and_duplicates(self, client, authenticated_headers, sample_device_profile_data):
        """Test that custom headers preserve order and allow duplicates."""
        # Test order preservation
        ordered_headers = [
            {"name": "X-First", "value": "first"},
            {"name": "X-Second", "value": "second"},
            {"name": "X-Third", "value": "third"},
        ]
        
        profile_data = sample_device_profile_data.copy()
        profile_data["custom_headers"] = ordered_headers
        profile_data["name"] = "Order Test Profile"
        
        response = client.post(
            "/api/v1/device-profiles",
            json=profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        response_headers = response.json()["custom_headers"]
        assert len(response_headers) == 3
        assert response_headers[0]["name"] == "X-First"
        assert response_headers[1]["name"] == "X-Second"
        assert response_headers[2]["name"] == "X-Third"
        
        # Test duplicate headers (should be allowed)
        duplicate_headers = [
            {"name": "X-Duplicate", "value": "first"},
            {"name": "X-Duplicate", "value": "second"},
            {"name": "X-Duplicate", "value": "third"},
        ]
        
        profile_data = sample_device_profile_data.copy()
        profile_data["custom_headers"] = duplicate_headers
        profile_data["name"] = "Duplicate Test Profile"
        
        response = client.post(
            "/api/v1/device-profiles",
            json=profile_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        response_headers = response.json()["custom_headers"]
        assert len(response_headers) == 3
        assert all(header["name"] == "X-Duplicate" for header in response_headers)
        assert response_headers[0]["value"] == "first"
        assert response_headers[1]["value"] == "second"
        assert response_headers[2]["value"] == "third"
