"""
Error handling and Problem+JSON responses for ZenRows Device Profile API.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ProblemDetail(BaseModel):
    """Problem+JSON response format."""
    
    type: str
    title: str
    status: int
    detail: str
    instance: str
    request_id: Optional[str] = None


def create_problem_detail(
    request: Request,
    status_code: int,
    title: str,
    detail: str,
    error_type: str = "about:blank"
) -> ProblemDetail:
    """
    Create a Problem+JSON response detail.
    
    Args:
        request: FastAPI request object
        status_code: HTTP status code
        title: Error title
        detail: Error detail
        error_type: Error type URI
        
    Returns:
        ProblemDetail: Problem detail object
    """
    return ProblemDetail(
        type=error_type,
        title=title,
        status=status_code,
        detail=detail,
        instance=str(request.url),
        request_id=request.headers.get("X-Request-ID")
    )


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions with Problem+JSON format.
    
    Args:
        request: FastAPI request object
        exc: HTTP exception
        
    Returns:
        JSONResponse: Problem+JSON response
    """
    problem_detail = create_problem_detail(
        request=request,
        status_code=exc.status_code,
        title=exc.detail,
        detail=exc.detail
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_detail.model_dump(),
        headers={"Content-Type": "application/problem+json"}
    )


def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle validation exceptions with Problem+JSON format.
    
    Args:
        request: FastAPI request object
        exc: Validation exception
        
    Returns:
        JSONResponse: Problem+JSON response
    """
    problem_detail = create_problem_detail(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        title="Validation Error",
        detail="Request validation failed",
        error_type="https://zenrows.com/problems/validation-error"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=problem_detail.model_dump(),
        headers={"Content-Type": "application/problem+json"}
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, validation_exception_handler)
