"""
Device profile API endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_current_owner_id
from app.core.pagination import PaginationParams, create_link_header, get_pagination_params, paginate_results
from app.db import get_db
from app.repositories.device_profile import DeviceProfileRepository
from app.schemas.device_profile import (
    DeviceProfileCreate,
    DeviceProfileList,
    DeviceProfileResponse,
    DeviceProfileUpdate
)

router = APIRouter()


@router.get("/device-profiles", response_model=DeviceProfileList)
async def list_device_profiles(
    request: Request,
    pagination: PaginationParams = Depends(get_pagination_params),
    owner_id: UUID = Depends(get_current_owner_id),
    db: Session = Depends(get_db)
):
    """List device profiles for the authenticated owner."""
    repository = DeviceProfileRepository(db)
    profiles, total_count = repository.list(owner_id, pagination.limit, pagination.offset)
    
    # Convert to response models
    profile_responses = [DeviceProfileResponse.model_validate(profile) for profile in profiles]
    
    # Create paginated response
    paginated_profiles, metadata = paginate_results(
        profile_responses, pagination.limit, pagination.offset, total_count
    )
    
    # Create Link header
    link_header = create_link_header(
        str(request.url).split('?')[0],  # Base URL without query params
        pagination.limit,
        pagination.offset,
        total_count
    )
    
    response_data = {
        "items": paginated_profiles,
        **metadata
    }
    
    response = JSONResponse(content=response_data)
    if link_header:
        response.headers["Link"] = link_header
    
    return response


@router.post("/device-profiles", response_model=DeviceProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_device_profile(
    profile_data: DeviceProfileCreate,
    owner_id: UUID = Depends(get_current_owner_id),
    db: Session = Depends(get_db)
):
    """Create a new device profile."""
    repository = DeviceProfileRepository(db)
    
    # Check for duplicate name
    if repository.check_name_exists(owner_id, profile_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile with name '{profile_data.name}' already exists"
        )
    
    profile = repository.create(owner_id, profile_data)
    return DeviceProfileResponse.model_validate(profile)


@router.get("/device-profiles/{profile_id}", response_model=DeviceProfileResponse)
async def get_device_profile(
    profile_id: UUID,
    owner_id: UUID = Depends(get_current_owner_id),
    db: Session = Depends(get_db)
):
    """Get a device profile by ID."""
    repository = DeviceProfileRepository(db)
    profile = repository.get_by_id(owner_id, profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device profile not found"
        )
    
    response = JSONResponse(content=DeviceProfileResponse.model_validate(profile).model_dump())
    response.headers["ETag"] = f'W/"{profile.version}"'
    
    return response


@router.patch("/device-profiles/{profile_id}", response_model=DeviceProfileResponse)
async def update_device_profile(
    profile_id: UUID,
    profile_data: DeviceProfileUpdate,
    request: Request,
    owner_id: UUID = Depends(get_current_owner_id),
    db: Session = Depends(get_db)
):
    """Update a device profile."""
    # Check for If-Match header
    if_match = request.headers.get("If-Match")
    if not if_match:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="If-Match header required for updates"
        )
    
    # Extract version from ETag
    try:
        version = int(if_match.replace('W/"', '').replace('"', ''))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid If-Match header format"
        )
    
    repository = DeviceProfileRepository(db)
    
    # Check for duplicate name if name is being updated
    if profile_data.name and repository.check_name_exists(owner_id, profile_data.name, profile_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile with name '{profile_data.name}' already exists"
        )
    
    profile = repository.update(owner_id, profile_id, profile_data, version)
    
    if not profile:
        # Check if profile exists
        existing_profile = repository.get_by_id(owner_id, profile_id)
        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device profile not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"Version mismatch. Current version: {existing_profile.version}"
            )
    
    response = JSONResponse(content=DeviceProfileResponse.model_validate(profile).model_dump())
    response.headers["ETag"] = f'W/"{profile.version}"'
    
    return response


@router.delete("/device-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device_profile(
    profile_id: UUID,
    owner_id: UUID = Depends(get_current_owner_id),
    db: Session = Depends(get_db)
):
    """Delete a device profile (soft delete)."""
    repository = DeviceProfileRepository(db)
    
    if not repository.soft_delete(owner_id, profile_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device profile not found"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
