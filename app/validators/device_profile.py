"""
Device profile validation utilities for ZenRows API.

This module contains validation logic for device profile fields that require
cross-field validation or complex business rules.
"""


def validate_country_code(country: str) -> str:
    """Validate country code format."""
    if country is not None:
        if not country.isalpha():
            raise ValueError('Country code must contain only letters')
        if not country.islower():
            raise ValueError('Country code must be lowercase')
    return country


def validate_window_size_for_device_type(width: int, height: int, device_type: str) -> None:
    """
    Validate window size based on device type (cross-field validation).
    
    This function is used for validation that requires access to multiple fields
    and cannot be easily expressed as a single field validator.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        device_type: Device type (desktop or mobile)
        
    Raises:
        ValueError: If window size is invalid for the device type
    """
    # Cross-field validation for mobile devices
    if device_type == "mobile":
        # Reject ultra-wide viewports for mobile
        if width > 2000 or height > 2000:
            raise ValueError("Mobile devices should not have ultra-wide viewports")
        
        # Reject landscape-oriented mobile with very wide aspect ratio
        if width > height and width / height > 3:
            raise ValueError("Mobile devices should not have ultra-wide aspect ratios")
