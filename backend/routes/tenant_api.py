"""
White-label Multi-tenant Business Directory API
Following the master project specifications exactly
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import hashlib
import secrets
from datetime import datetime, timedelta

from database import get_db
from database.tenant_models import Tenant, User, Listing, Category, Endorsement, UsageMeter
from backend.schemas.tenant_schemas import (
    AuthRegister, AuthLogin, AuthResponse, TenantResponse, UserResponse,
    ListingCreate, ListingUpdate, ListingResponse, SearchRequest, SearchResponse,
    EndorsementCreate, EndorsementResponse, UsageResponse, HealthResponse,
    ApiKeyResponse, ErrorResponse
)
from backend.core.config import settings

router = APIRouter(prefix="/v1", tags=["tenant-api"])
security = HTTPBearer()


# Authentication Dependencies
def get_current_tenant(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current tenant from API key or JWT token"""
    token = credentials.credentials
    
    # Check if it's an API key (starts with sk_)
    if token.startswith("sk_"):
        # Hash the API key and look up tenant
        api_key_hash = hashlib.sha256(token.encode()).hexdigest()
        tenant = db.query(Tenant).filter(Tenant.api_key_hash == api_key_hash).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        return tenant
    
    # TODO: Implement JWT token validation
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )


def get_current_user(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    # TODO: Implement JWT user validation
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User authentication not implemented"
    )


# Auth Endpoints
@router.post("/auth/register", response_model=AuthResponse)
async def register(
    auth_data: AuthRegister,
    db: Session = Depends(get_db)
):
    """Register new tenant owner"""
    # Check if tenant slug already exists
    existing_tenant = db.query(Tenant).filter(Tenant.slug == auth_data.tenant_slug).first()
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant slug already exists"
        )
    
    # Check if user email already exists
    existing_user = db.query(User).filter(User.email == auth_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create tenant
    api_key = f"sk_{secrets.token_urlsafe(32)}"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    tenant = Tenant(
        slug=auth_data.tenant_slug,
        name=auth_data.tenant_name,
        api_key_hash=api_key_hash,
        plan="free",
        plan_status="active"
    )
    db.add(tenant)
    db.flush()  # Get tenant ID
    
    # Create user
    password_hash = hashlib.sha256(auth_data.password.encode()).hexdigest()  # TODO: Use proper password hashing
    user = User(
        email=auth_data.email,
        pw_hash=password_hash,
        role="owner",
        tenant_id=tenant.id
    )
    db.add(user)
    db.commit()
    
    # TODO: Generate JWT token
    access_token = "jwt_token_placeholder"
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user),
        tenant=TenantResponse.from_orm(tenant)
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(
    auth_data: AuthLogin,
    db: Session = Depends(get_db)
):
    """Login tenant owner"""
    user = db.query(User).filter(User.email == auth_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # TODO: Verify password hash
    password_hash = hashlib.sha256(auth_data.password.encode()).hexdigest()
    if user.pw_hash != password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    
    # TODO: Generate JWT token
    access_token = "jwt_token_placeholder"
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user),
        tenant=TenantResponse.from_orm(tenant)
    )


# Tenant Endpoints
@router.get("/tenants/me", response_model=TenantResponse)
async def get_tenant_me(
    tenant: Tenant = Depends(get_current_tenant)
):
    """Get current tenant information"""
    return TenantResponse.from_orm(tenant)


@router.post("/tenants/{tenant_id}/apikey/rotate", response_model=ApiKeyResponse)
async def rotate_api_key(
    tenant_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Rotate API key for tenant (owner only)"""
    if tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Generate new API key
    api_key = f"sk_{secrets.token_urlsafe(32)}"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Update tenant
    tenant.api_key_hash = api_key_hash
    db.commit()
    
    return ApiKeyResponse(
        api_key=api_key,
        created_at=datetime.utcnow()
    )


# Listing Endpoints
@router.post("/listings", response_model=ListingResponse)
async def create_listing(
    listing_data: ListingCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Create new business listing"""
    # Generate slug from name
    slug = listing_data.name.lower().replace(" ", "-").replace("&", "and")
    
    listing = Listing(
        tenant_id=tenant.id,
        name=listing_data.name,
        slug=slug,
        description=listing_data.description,
        website=listing_data.website,
        phone=listing_data.phone,
        email=listing_data.email,
        addr_line1=listing_data.addr_line1,
        city=listing_data.city,
        region=listing_data.region,
        postal=listing_data.postal,
        country=listing_data.country,
        lat=listing_data.lat,
        lng=listing_data.lng,
        category_id=listing_data.category_id,
        tags=listing_data.tags,
        hours_json=listing_data.hours_json,
        images_json=listing_data.images_json,
        status="active"
    )
    
    db.add(listing)
    db.commit()
    db.refresh(listing)
    
    return ListingResponse.from_orm(listing)


@router.get("/listings", response_model=SearchResponse)
async def search_listings(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[int] = Query(None, description="Category ID filter"),
    lat: Optional[float] = Query(None, description="Latitude for geo search"),
    lng: Optional[float] = Query(None, description="Longitude for geo search"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers"),
    sort: str = Query("relevance", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Search business listings with filters and geo search"""
    query = db.query(Listing).filter(Listing.tenant_id == tenant.id)
    
    # Text search
    if q:
        query = query.filter(
            (Listing.name.ilike(f"%{q}%")) |
            (Listing.description.ilike(f"%{q}%"))
        )
    
    # Category filter
    if category:
        query = query.filter(Listing.category_id == category)
    
    # Geo search (simplified - would need PostGIS for proper implementation)
    if lat and lng and radius_km:
        # TODO: Implement proper geo search with PostGIS
        pass
    
    # Count total
    total = query.count()
    
    # Apply sorting
    if sort == "name":
        query = query.order_by(Listing.name)
    elif sort == "created":
        query = query.order_by(Listing.created_at.desc())
    elif sort == "distance" and lat and lng:
        # TODO: Implement distance sorting
        query = query.order_by(Listing.name)
    else:  # relevance
        query = query.order_by(Listing.featured_until.desc().nulls_last(), Listing.created_at.desc())
    
    # Apply pagination
    offset = (page - 1) * limit
    listings = query.offset(offset).limit(limit).all()
    
    return SearchResponse(
        listings=[ListingResponse.from_orm(listing) for listing in listings],
        total=total,
        page=page,
        limit=limit,
        has_next=(offset + limit) < total
    )


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Get specific business listing"""
    listing = db.query(Listing).filter(
        Listing.id == listing_id,
        Listing.tenant_id == tenant.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    return ListingResponse.from_orm(listing)


@router.put("/listings/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    listing_data: ListingUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Update business listing"""
    listing = db.query(Listing).filter(
        Listing.id == listing_id,
        Listing.tenant_id == tenant.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Update fields
    for field, value in listing_data.dict(exclude_unset=True).items():
        setattr(listing, field, value)
    
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    
    return ListingResponse.from_orm(listing)


@router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Delete business listing"""
    listing = db.query(Listing).filter(
        Listing.id == listing_id,
        Listing.tenant_id == tenant.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    db.delete(listing)
    db.commit()
    
    return {"message": "Listing deleted successfully"}


# Endorsement Endpoints
@router.post("/endorsements", response_model=EndorsementResponse)
async def create_endorsement(
    endorsement_data: EndorsementCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Create customer endorsement"""
    # Generate anti-spam transaction hash
    txn_hash = hashlib.sha256(f"{endorsement_data.listing_id}{datetime.utcnow().isoformat()}".encode()).hexdigest()
    
    endorsement = Endorsement(
        tenant_id=tenant.id,
        listing_id=endorsement_data.listing_id,
        would_repeat=endorsement_data.would_repeat,
        tags=endorsement_data.tags,
        comment=endorsement_data.comment,
        txn_hash=txn_hash,
        ip_hash="hashed_ip_placeholder"  # TODO: Get real IP and hash it
    )
    
    db.add(endorsement)
    db.commit()
    db.refresh(endorsement)
    
    return EndorsementResponse.from_orm(endorsement)


@router.get("/endorsements", response_model=List[EndorsementResponse])
async def get_endorsements(
    listing_id: Optional[int] = Query(None, description="Filter by listing ID"),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Get endorsements with optional listing filter"""
    query = db.query(Endorsement).filter(Endorsement.tenant_id == tenant.id)
    
    if listing_id:
        query = query.filter(Endorsement.listing_id == listing_id)
    
    endorsements = query.order_by(Endorsement.created_at.desc()).all()
    
    return [EndorsementResponse.from_orm(endorsement) for endorsement in endorsements]


# Media Upload Endpoint
@router.post("/media/upload")
async def upload_media(
    tenant: Tenant = Depends(get_current_tenant)
):
    """Upload media files (signed URL or direct)"""
    # TODO: Implement S3 signed URL generation
    return {"upload_url": "s3_signed_url_placeholder", "expires_in": 3600}


# Billing Endpoints
@router.post("/billing/checkout-session")
async def create_checkout_session(
    plan: str,
    tenant: Tenant = Depends(get_current_tenant)
):
    """Create Stripe checkout session for plan upgrade"""
    # TODO: Implement Stripe checkout session creation
    return {"checkout_url": "stripe_checkout_url_placeholder"}


@router.post("/billing/webhook")
async def stripe_webhook(
    # TODO: Implement Stripe webhook handling
    request_data: dict = None
):
    """Handle Stripe webhooks"""
    # TODO: Implement Stripe webhook handling
    return {"status": "webhook_received"}


# Usage Endpoints
@router.get("/usage/me", response_model=UsageResponse)
async def get_usage(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Get current tenant usage metrics"""
    current_month = datetime.utcnow().strftime("%Y-%m")
    
    usage = db.query(UsageMeter).filter(
        UsageMeter.tenant_id == tenant.id,
        UsageMeter.month == current_month
    ).first()
    
    if not usage:
        usage = UsageMeter(
            tenant_id=tenant.id,
            month=current_month,
            api_calls=0,
            listings_count=0,
            members_count=0,
            storage_mb=0
        )
        db.add(usage)
        db.commit()
    
    return UsageResponse.from_orm(usage)


# Health Check Endpoint
@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database=True,  # TODO: Check database connection
        redis=True,     # TODO: Check Redis connection
        storage=True    # TODO: Check storage connection
    )
