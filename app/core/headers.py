"""
Header validation utilities for ZenRows Device Profile API.
"""

from typing import Dict, List, Set

# Hop-by-hop headers that should be rejected
FORBIDDEN_HEADERS: Set[str] = {
    "host",
    "content-length",
    "connection",
    "transfer-encoding",
    "keep-alive",
    "upgrade",
    "trailer"
}


def validate_custom_headers(headers: List[Dict[str, str]]) -> None:
    """
    Validate custom headers for forbidden names.
    
    Args:
        headers: List of header dictionaries with 'name' and 'value' keys
        
    Raises:
        ValueError: If forbidden headers are present
    """
    if not headers:
        return
    
    forbidden_found = []
    
    for header in headers:
        if not isinstance(header, dict):
            raise ValueError("Headers must be a list of objects with 'name' and 'value' keys")
        
        if "name" not in header or "value" not in header:
            raise ValueError("Each header must have 'name' and 'value' keys")
        
        header_name = header["name"].lower()
        if header_name in FORBIDDEN_HEADERS:
            forbidden_found.append(header_name)
    
    if forbidden_found:
        raise ValueError(f"Forbidden headers found: {', '.join(forbidden_found)}")


def validate_country_code(country: str) -> None:
    """
    Validate country code format.
    
    Args:
        country: Country code to validate
        
    Raises:
        ValueError: If country code is invalid
    """
    if not country:
        return
    
    if not isinstance(country, str):
        raise ValueError("Country must be a string")
    
    if len(country) != 2:
        raise ValueError("Country code must be exactly 2 characters")
    
    if not country.isalpha():
        raise ValueError("Country code must contain only letters")
    
    if not country.islower():
        raise ValueError("Country code must be lowercase")


def validate_window_size(width: int, height: int, device_type: str) -> None:
    """
    Validate window size based on device type.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        device_type: Device type (desktop or mobile)
        
    Raises:
        ValueError: If window size is invalid
    """
    if width < 100 or width > 10000:
        raise ValueError("Window width must be between 100 and 10000 pixels")
    
    if height < 100 or height > 10000:
        raise ValueError("Window height must be between 100 and 10000 pixels")
    
    # Cross-field validation for mobile devices
    if device_type == "mobile":
        # Reject ultra-wide viewports for mobile
        if width > 2000 or height > 2000:
            raise ValueError("Mobile devices should not have ultra-wide viewports")
        
        # Reject landscape-oriented mobile with very wide aspect ratio
        if width > height and width / height > 3:
            raise ValueError("Mobile devices should not have ultra-wide aspect ratios")
