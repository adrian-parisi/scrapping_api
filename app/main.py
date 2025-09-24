"""
FastAPI application entry point for ZenRows Device Profile API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.errors import setup_exception_handlers
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_size import RequestSizeMiddleware
from app.routers import device_profiles, templates, health

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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(device_profiles.router, prefix="/api/v1", tags=["device-profiles"])
app.include_router(templates.router, prefix="/api/v1", tags=["templates"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "ZenRows Device Profile API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
