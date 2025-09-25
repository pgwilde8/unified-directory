"""
Business management routes for Business Directory
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import json
import os

from database import get_db
from database.business_models import User, Business, BusinessReview, BusinessCategory
from backend.routes.google_auth import get_current_user

router = APIRouter()


class BusinessCreate(BaseModel):
    """Business creation request"""
    name: str
    description: Optional[str] = None
    category: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    hours: Optional[dict] = None
    price_range: Optional[str] = None
    amenities: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class BusinessUpdate(BaseModel):
    """Business update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    hours: Optional[dict] = None
    price_range: Optional[str] = None
    amenities: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class BusinessResponse(BaseModel):
    """Business response"""
    id: int
    name: str
    description: Optional[str]
    category: str
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    hours: Optional[dict]
    price_range: Optional[str]
    amenities: Optional[List[str]]
    tags: Optional[List[str]]
    logo_url: Optional[str]
    images: Optional[List[str]]
    is_approved: bool
    is_featured: bool
    is_active: bool
    slug: str
    created_at: datetime
    updated_at: datetime


@router.get("/my-businesses")
async def get_my_businesses(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's businesses"""
    businesses = db.query(Business).filter(
        Business.owner_id == current_user["id"],
        Business.is_active == True
    ).all()
    
    return [
        BusinessResponse(
            id=business.id,
            name=business.name,
            description=business.description,
            category=business.category,
            phone=business.phone,
            email=business.email,
            website=business.website,
            address=business.address,
            city=business.city,
            state=business.state,
            zip_code=business.zip_code,
            hours=business.hours,
            price_range=business.price_range,
            amenities=business.amenities,
            tags=business.tags,
            logo_url=business.logo_url,
            images=business.images,
            is_approved=business.is_approved,
            is_featured=business.is_featured,
            is_active=business.is_active,
            slug=business.slug,
            created_at=business.created_at,
            updated_at=business.updated_at
        )
        for business in businesses
    ]


@router.post("/create", response_model=BusinessResponse)
async def create_business(
    business_data: BusinessCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new business"""
    
    # Check if user has reached the limit
    existing_count = db.query(Business).filter(
        Business.owner_id == current_user["id"],
        Business.is_active == True
    ).count()
    
    if existing_count >= settings.MAX_BUSINESS_LISTINGS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_BUSINESS_LISTINGS_PER_USER} businesses allowed per user"
        )
    
    # Validate category
    allowed_categories = settings.ALLOWED_BUSINESS_CATEGORIES.split(",")
    if business_data.category not in allowed_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Allowed categories: {', '.join(allowed_categories)}"
        )
    
    # Create slug from name
    slug = _create_slug(business_data.name)
    
    # Check if slug already exists
    existing_slug = db.query(Business).filter(Business.slug == slug).first()
    if existing_slug:
        slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create business
    business = Business(
        owner_id=current_user["id"],
        name=business_data.name,
        description=business_data.description,
        category=business_data.category,
        phone=business_data.phone,
        email=business_data.email,
        website=business_data.website,
        address=business_data.address,
        city=business_data.city,
        state=business_data.state,
        zip_code=business_data.zip_code,
        hours=business_data.hours,
        price_range=business_data.price_range,
        amenities=business_data.amenities,
        tags=business_data.tags,
        slug=slug,
        is_approved=not settings.BUSINESS_APPROVAL_REQUIRED,  # Auto-approve if approval not required
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(business)
    db.commit()
    db.refresh(business)
    
    return BusinessResponse(
        id=business.id,
        name=business.name,
        description=business.description,
        category=business.category,
        phone=business.phone,
        email=business.email,
        website=business.website,
        address=business.address,
        city=business.city,
        state=business.state,
        zip_code=business.zip_code,
        hours=business.hours,
        price_range=business.price_range,
        amenities=business.amenities,
        tags=business.tags,
        logo_url=business.logo_url,
        images=business.images,
        is_approved=business.is_approved,
        is_featured=business.is_featured,
        is_active=business.is_active,
        slug=business.slug,
        created_at=business.created_at,
        updated_at=business.updated_at
    )


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: int,
    business_data: BusinessUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a business"""
    
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == current_user["id"],
        Business.is_active == True
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Update fields
    update_data = business_data.dict(exclude_unset=True)
    
    # Validate category if provided
    if "category" in update_data:
        allowed_categories = settings.ALLOWED_BUSINESS_CATEGORIES.split(",")
        if update_data["category"] not in allowed_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Allowed categories: {', '.join(allowed_categories)}"
            )
    
    # Update slug if name changed
    if "name" in update_data and update_data["name"] != business.name:
        new_slug = _create_slug(update_data["name"])
        existing_slug = db.query(Business).filter(
            Business.slug == new_slug,
            Business.id != business_id
        ).first()
        if existing_slug:
            new_slug = f"{new_slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        update_data["slug"] = new_slug
    
    # Update business
    for field, value in update_data.items():
        setattr(business, field, value)
    
    business.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(business)
    
    return BusinessResponse(
        id=business.id,
        name=business.name,
        description=business.description,
        category=business.category,
        phone=business.phone,
        email=business.email,
        website=business.website,
        address=business.address,
        city=business.city,
        state=business.state,
        zip_code=business.zip_code,
        hours=business.hours,
        price_range=business.price_range,
        amenities=business.amenities,
        tags=business.tags,
        logo_url=business.logo_url,
        images=business.images,
        is_approved=business.is_approved,
        is_featured=business.is_featured,
        is_active=business.is_active,
        slug=business.slug,
        created_at=business.created_at,
        updated_at=business.updated_at
    )


@router.delete("/{business_id}")
async def delete_business(
    business_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a business (soft delete)"""
    
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == current_user["id"],
        Business.is_active == True
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    business.is_active = False
    business.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Business deleted successfully"}


@router.post("/{business_id}/upload-logo")
async def upload_logo(
    business_id: int,
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload business logo"""
    
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == current_user["id"],
        Business.is_active == True
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Validate file type
    allowed_types = settings.ALLOWED_FILE_TYPES.split(",")
    file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Validate file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIRECTORY, f"businesses/{business_id}")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate filename
    filename = f"logo_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update business logo URL
    logo_url = f"/static/uploads/businesses/{business_id}/{filename}"
    business.logo_url = logo_url
    business.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"logo_url": logo_url, "message": "Logo uploaded successfully"}


def _create_slug(name: str) -> str:
    """Create URL-friendly slug from business name"""
    import re
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')
