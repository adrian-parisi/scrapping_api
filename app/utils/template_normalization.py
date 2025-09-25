"""
Schema migration utilities for device profile templates.

This module handles the normalization of template payloads to ensure compatibility
with the current device profile schema, supporting breaking changes and field migrations.
"""

from typing import Dict, Any, Callable


class TemplateNormalizer:
    """Handles normalization of device profile templates."""
    
    def __init__(self):
        """Initialize the template normalizer with field mappings and defaults."""
        # Field mapping for schema changes
        # Add field mappings here as schema evolves
        self.field_mappings: Dict[str, str | Callable] = {
            # "old_field_name": "new_field_name",  # Simple field rename
            # "old_field_name": self._migrate_old_field,  # Custom migration function
        }
        
        # Default values for required fields
        # Add new required fields here as schema evolves
        self.defaults: Dict[str, Any] = {
            "device_type": "desktop",
            "window_width": 1920,
            "window_height": 1080,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "country": "us",
            "custom_headers": [],
            "extras": {},
        }
    
    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize template payload to comply with the latest schema.
        
        This function transforms the payload to ensure compatibility with the current
        device profile schema, handling any breaking changes or missing fields.
        
        Args:
            payload: Raw template payload data
            
        Returns:
            dict: Normalized payload compliant with latest schema
        """
        # Start with a copy to avoid modifying the original
        normalized = payload.copy()
        
        # Apply field mappings
        for old_field, new_field in self.field_mappings.items():
            if old_field in normalized:
                if callable(new_field):
                    # Custom migration function
                    normalized = new_field(normalized)
                else:
                    # Simple field rename
                    normalized[new_field] = normalized.pop(old_field)
        
        # Apply defaults for missing fields
        for field, default_value in self.defaults.items():
            if field not in normalized:
                normalized[field] = default_value
        
        return normalized
    
    def add_field_mapping(self, old_field: str, new_field: str | Callable) -> None:
        """
        Add a new field mapping for schema migration.
        
        Args:
            old_field: Name of the old field
            new_field: Name of the new field or migration function
        """
        self.field_mappings[old_field] = new_field
    
    def add_default(self, field: str, default_value: Any) -> None:
        """
        Add a default value for a required field.
        
        Args:
            field: Name of the field
            default_value: Default value to use if field is missing
        """
        self.defaults[field] = default_value


# Global instance for use across the application
template_normalizer = TemplateNormalizer()
