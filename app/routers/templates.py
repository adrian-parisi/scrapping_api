"""
Template API endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.auth import get_current_owner_id
from app.db import get_db
from app.repositories.device_profile import DeviceProfileRepository
from app.repositories.template import TemplateRepository
from app.schemas.device_profile import DeviceProfileCreate, DeviceProfileResponse
from app.schemas.template import CreateProfileFromTemplateRequest, TemplateResponse

router = APIRouter()


@router.get("/templates", response_model=Page[TemplateResponse])
async def list_templates(
    params: Params = Depends(),
    db: Session = Depends(get_db)
):
    """List all templates."""
    repository = TemplateRepository(db)
    
    # Get the base query from repository
    query = repository.get_query()
    
    # Use fastapi-pagination to handle pagination automatically
    return paginate(
        query,
        params,
        transformer=lambda items: [TemplateResponse.model_validate(item) for item in items]
    )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a template by ID."""
    repository = TemplateRepository(db)
    template = repository.get_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateResponse.model_validate(template)


@router.post("/templates/{template_id}/create-profile", response_model=DeviceProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile_from_template(
    template_id: UUID,
    overrides: CreateProfileFromTemplateRequest,
    owner_id: UUID = Depends(get_current_owner_id),
    db: Session = Depends(get_db)
):
    """Create a device profile from a template."""
    template_repository = TemplateRepository(db)
    profile_repository = DeviceProfileRepository(db)
    
    # Get template data with overrides
    profile_data_dict = template_repository.create_profile_from_template(owner_id, template_id, overrides)
    
    if not profile_data_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Convert to DeviceProfileCreate schema
    profile_data = DeviceProfileCreate(**profile_data_dict)
    
    # Check for duplicate name
    if profile_repository.check_name_exists(owner_id, profile_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile with name '{profile_data.name}' already exists"
        )
    
    # Create the profile
    profile = profile_repository.create(owner_id, profile_data)
    
    response = JSONResponse(content=DeviceProfileResponse.model_validate(profile).model_dump())
    response.headers["Location"] = f"/api/v1/device-profiles/{profile.id}"
    
    return response