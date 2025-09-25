"""
Device profile validation utilities for ZenRows API.

This module contains validation logic for device profile fields that require
cross-field validation or complex business rules.
"""

from typing import Dict, List
import pycountry


def validate_country_code(country: str) -> str:
    """
    Validate country code using pycountry library (ISO 3166-1).
    
    Args:
        country: Country code to validate (e.g., 'us', 'gb', 'fr')
        
    Returns:
        str: Validated country code in lowercase
        
    Raises:
        ValueError: If country code is invalid
    """
    if country is None:
        return country
    
    country = country.lower()
    
    # Validate against ISO 3166-1 country codes
    if not pycountry.countries.get(alpha_2=country):
        raise ValueError(f"Invalid country code: {country}")
    
    return country


def validate_custom_headers(headers: List) -> List:
    """
    Validate custom headers and reject forbidden ones.
    
    Args:
        headers: List of CustomHeader objects
        
    Returns:
        List: Validated headers list
        
    Raises:
        ValueError: If forbidden headers are found
    """
    # Forbidden headers that should not be set by clients
    # TODO: Validate with ZenRows team if these forbidden headers make sense
    FORBIDDEN_HEADERS = {
        # Hop-by-hop headers (RFC 2616) - these are meaningful only for a single transport-level connection
        'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
        'te', 'trailers', 'transfer-encoding', 'upgrade',
        
        # Controlled headers (managed by HTTP implementation) - these are controlled by the HTTP implementation
        'host', 'content-length', 'content-encoding', 'content-range', 'content-type'
    }
    
    for header in headers:
        name = header.name.lower().strip()
        if not name:
            raise ValueError("Header name cannot be empty")
        
        if name in FORBIDDEN_HEADERS:
            raise ValueError(f"Forbidden header: {name}")
    
    return headers


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
