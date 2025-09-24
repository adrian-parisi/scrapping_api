"""
Pagination utilities for ZenRows Device Profile API.
"""

from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

from fastapi import Query
from pydantic import BaseModel

from app.settings import settings


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    limit: int
    offset: int


def get_pagination_params(
    limit: Optional[int] = Query(
        default=settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Number of items to return"
    ),
    offset: Optional[int] = Query(
        default=0,
        ge=0,
        description="Number of items to skip"
    )
) -> PaginationParams:
    """
    Get pagination parameters from query string.
    
    Args:
        limit: Number of items to return
        offset: Number of items to skip
        
    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(limit=limit, offset=offset)


def create_link_header(
    request_url: str,
    limit: int,
    offset: int,
    total_count: int
) -> Optional[str]:
    """
    Create Link header for pagination.
    
    Args:
        request_url: Base request URL
        limit: Number of items per page
        offset: Current offset
        total_count: Total number of items
        
    Returns:
        Optional[str]: Link header value or None
    """
    links = []
    
    # Next page
    if offset + limit < total_count:
        next_offset = offset + limit
        next_params = {"limit": limit, "offset": next_offset}
        next_url = f"{request_url}?{urlencode(next_params)}"
        links.append(f'<{next_url}>; rel="next"')
    
    # Previous page
    if offset > 0:
        prev_offset = max(0, offset - limit)
        prev_params = {"limit": limit, "offset": prev_offset}
        prev_url = f"{request_url}?{urlencode(prev_params)}"
        links.append(f'<{prev_url}>; rel="prev"')
    
    return ", ".join(links) if links else None


def paginate_results(
    results: List,
    limit: int,
    offset: int,
    total_count: int
) -> Tuple[List, Dict[str, int]]:
    """
    Paginate query results.
    
    Args:
        results: Query results
        limit: Number of items per page
        offset: Current offset
        total_count: Total number of items
        
    Returns:
        Tuple[List, Dict[str, int]]: Paginated results and metadata
    """
    # Apply pagination
    paginated_results = results[offset:offset + limit]
    
    # Calculate metadata
    metadata = {
        "limit": limit,
        "offset": offset,
        "total": total_count,
        "count": len(paginated_results)
    }
    
    return paginated_results, metadata
