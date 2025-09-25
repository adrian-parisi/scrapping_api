"""
Tests for template payload normalization functionality.
"""

import pytest
from unittest.mock import Mock

from app.utils.template_normalization import TemplateNormalizer


class TestTemplateNormalization:
    """Test template payload normalization."""
    
    def test_normalize_basic_payload(self):
        """Test normalizing a basic template payload."""
        normalizer = TemplateNormalizer()
        
        # Test payload
        payload = {
            "name": "Chrome Profile",
            "device_type": "desktop",
            "user_agent": "Mozilla/5.0...",
            "country": "us"
        }
        
        # Normalize the payload
        normalized = normalizer.normalize_payload(payload)
        
        # Verify required fields are preserved
        assert normalized["name"] == "Chrome Profile"
        assert normalized["device_type"] == "desktop"
        assert normalized["user_agent"] == "Mozilla/5.0..."
        assert normalized["country"] == "us"
        
        # Verify default fields are added
        assert normalized["window_width"] == 1920
        assert normalized["window_height"] == 1080
        assert normalized["custom_headers"] == []
        assert normalized["extras"] == {}
    
    def test_normalize_missing_required_fields(self):
        """Test normalizing payload with missing required fields."""
        normalizer = TemplateNormalizer()
        
        # Minimal payload missing required fields
        payload = {
            "name": "Minimal Profile"
        }
        
        normalized = normalizer.normalize_payload(payload)
        
        # Verify defaults are applied
        assert normalized["device_type"] == "desktop"
        assert normalized["user_agent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        assert normalized["country"] == "us"
        assert normalized["window_width"] == 1920
        assert normalized["window_height"] == 1080
        assert normalized["custom_headers"] == []
        assert normalized["extras"] == {}
    
    def test_normalize_preserves_existing_values(self):
        """Test that normalization preserves existing valid values."""
        normalizer = TemplateNormalizer()
        
        # Payload with all fields already present
        payload = {
            "name": "Complete Profile",
            "device_type": "mobile",
            "window_width": 800,
            "window_height": 600,
            "user_agent": "Custom Agent",
            "country": "gb",
            "custom_headers": [{"name": "X-Custom", "value": "test"}],
            "extras": {"browser": "safari"}
        }
        
        normalized = normalizer.normalize_payload(payload)
        
        # Verify all existing values are preserved
        assert normalized["name"] == "Complete Profile"
        assert normalized["device_type"] == "mobile"
        assert normalized["window_width"] == 800
        assert normalized["window_height"] == 600
        assert normalized["user_agent"] == "Custom Agent"
        assert normalized["country"] == "gb"
        assert normalized["custom_headers"] == [{"name": "X-Custom", "value": "test"}]
        assert normalized["extras"] == {"browser": "safari"}
    
    def test_normalize_does_not_modify_original(self):
        """Test that normalization doesn't modify the original payload."""
        normalizer = TemplateNormalizer()
        
        original_payload = {
            "name": "Original Profile",
            "device_type": "desktop"
        }
        
        # Normalize the payload
        normalized = normalizer.normalize_payload(original_payload)
        
        # Verify original is unchanged
        assert "window_width" not in original_payload
        assert "window_height" not in original_payload
        
        # Verify normalized has the defaults
        assert "window_width" in normalized
        assert "window_height" in normalized
    
    def test_template_normalizer_extensibility(self):
        """Test that template normalizer can be extended with new mappings and defaults."""
        normalizer = TemplateNormalizer()
        
        # Add a new field mapping
        normalizer.add_field_mapping("old_field", "new_field")
        
        # Add a new default
        normalizer.add_default("new_required_field", "default_value")
        
        # Test payload with old field
        payload = {
            "name": "Test Profile",
            "old_field": "test_value"
        }
        
        normalized = normalizer.normalize_payload(payload)
        
        # Verify field mapping worked
        assert "old_field" not in normalized
        assert normalized["new_field"] == "test_value"
        
        # Verify new default was applied
        assert normalized["new_required_field"] == "default_value"
    
    def test_template_schema_compatibility_break_detection(self):
        """Test that detects when device profile schema changes break existing templates."""
        from app.schemas.device_profile import DeviceProfileCreate
        from pydantic import ValidationError
        
        normalizer = TemplateNormalizer()
        
        # Create a template with current valid schema (snapshot)
        current_valid_template = {
            "name": "Chrome Desktop",
            "device_type": "desktop",
            "window_width": 1920,
            "window_height": 1080,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "country": "us",
            "custom_headers": [],
            "extras": {}
        }
        
        # Normalize the template
        normalized = normalizer.normalize_payload(current_valid_template)
        
        # This should NOT raise ValidationError - template should be valid
        try:
            DeviceProfileCreate(**normalized)
        except ValidationError as e:
            pytest.fail(f"Template schema compatibility broken! Current template is no longer valid: {e}")
        
        # Test with a template that has missing required fields (should be caught)
        incomplete_template = {
            "name": "Incomplete Template"
            # Missing required fields
        }
        
        normalized_incomplete = normalizer.normalize_payload(incomplete_template)
        
        # This should NOT raise ValidationError - normalization should add defaults
        try:
            DeviceProfileCreate(**normalized_incomplete)
        except ValidationError as e:
            pytest.fail(f"Template normalization failed to add required defaults: {e}")
        
        # Test with a template that has invalid field types (should be caught)
        invalid_type_template = {
            "name": "Invalid Type Template",
            "device_type": "invalid_device_type",  # Invalid enum value
            "window_width": "not_a_number",  # Should be int
            "window_height": "not_a_number",  # Should be int
            "user_agent": "Mozilla/5.0...",
            "country": "invalid_country",  # Invalid country code
            "custom_headers": "not_a_list",  # Should be list
            "extras": "not_a_dict"  # Should be dict
        }
        
        normalized_invalid = normalizer.normalize_payload(invalid_type_template)
        
        # This SHOULD raise ValidationError - invalid types should be caught
        with pytest.raises(ValidationError) as exc_info:
            DeviceProfileCreate(**normalized_invalid)
        
        # Verify specific validation errors
        errors = exc_info.value.errors()
        error_fields = [error['loc'][0] for error in errors]
        
        # Should have validation errors for invalid fields
        assert 'device_type' in error_fields
        assert 'window_width' in error_fields
        assert 'window_height' in error_fields
        assert 'country' in error_fields
        assert 'custom_headers' in error_fields
        assert 'extras' in error_fields
    
    def test_real_template_schema_compatibility(self, test_templates):
        """Test that real templates from the database are compatible with current schema."""
        from app.schemas.device_profile import DeviceProfileCreate
        from pydantic import ValidationError
        
        normalizer = TemplateNormalizer()
        
        # Test each template for schema compatibility
        for template in test_templates:
            template_data = template.data
            
            # Normalize the template data
            normalized = normalizer.normalize_payload(template_data)
            
            # This should NOT raise ValidationError - real templates should be valid
            try:
                DeviceProfileCreate(**normalized)
            except ValidationError as e:
                pytest.fail(
                    f"Real template '{template.name}' (ID: {template.id}) is no longer "
                    f"compatible with current device profile schema! Error: {e}"
                )
