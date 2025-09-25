"""
FastAPI application entry point for ZenRows Device Profile API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from fastapi_problem.handler import add_exception_handler, new_exception_handler
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_size import RequestSizeMiddleware
from app.routers import device_profiles, templates

app = FastAPI(
    title="ZenRows Device Profile API",
    description="REST API for managing device profiles used in web scraping operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestSizeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For the sake of this technical interview, we'll allow all origins, but in production, it should be configured appropriately
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handling using fastapi-problem (handles all exceptions)
exception_handler = new_exception_handler()
add_exception_handler(app, exception_handler)

# Include routers
app.include_router(device_profiles.router, prefix="/api/v1", tags=["device-profiles"])
app.include_router(templates.router, prefix="/api/v1", tags=["templates"])

# Add pagination support
add_pagination(app)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "ZenRows Device Profile API",
        "version": "1.0.0",
        "docs": "/docs"
    }
