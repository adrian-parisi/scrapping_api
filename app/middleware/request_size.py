"""
Request size limiting middleware.
"""

from typing import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.settings import settings


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check request size and limit if necessary."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > settings.max_request_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
                        detail=f"Request body too large. Maximum size: {settings.max_request_size} bytes"
                    )
            except ValueError:
                # Invalid content-length header, let it pass
                pass
        
        # Process request
        response = await call_next(request)
        
        # Add size limit header to response
        response.headers["X-Request-Size-Limit"] = str(settings.max_request_size)
        
        return response
