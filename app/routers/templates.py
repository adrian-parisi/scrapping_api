"""
Template API endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_current_owner_id
from app.core.pagination import PaginationParams, create_link_header, get_pagination_params, paginate_results
from app.db import get_db
from app.repositories.device_profile import DeviceProfileRepository
from app.repositories.template import TemplateRepository
from app.schemas.device_profile import DeviceProfileCreate, DeviceProfileResponse
from app.schemas.template import CreateProfileFromTemplateRequest, TemplateList, TemplateResponse

router = APIRouter()


@router.get("/templates", response_model=TemplateList)
async def list_templates(
    request: Request,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    """List all templates."""
    repository = TemplateRepository(db)
    templates = repository.list()
    
    # Convert to response models
    template_responses = [TemplateResponse.model_validate(template) for template in templates]
    
    # Create paginated response
    paginated_templates, metadata = paginate_results(
        template_responses, pagination.limit, pagination.offset, len(templates)
    )
    
    # Create Link header
    link_header = create_link_header(
        str(request.url).split('?')[0],  # Base URL without query params
        pagination.limit,
        pagination.offset,
        len(templates)
    )
    
    response_data = {
        "items": paginated_templates,
        **metadata
    }
    
    response = JSONResponse(content=response_data)
    if link_header:
        response.headers["Link"] = link_header
    
    return response


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
