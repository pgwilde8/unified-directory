"""
Pydantic schemas for white-label multi-tenant Business Directory Platform
Following the master project specifications exactly
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlanEnum(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"


class PlanStatusEnum(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class RoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"


class StatusEnum(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"


# Tenant Schemas
class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    domain: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    theme: Optional[Dict[str, Any]] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    domain: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    theme: Optional[Dict[str, Any]] = None


class TenantResponse(TenantBase):
    id: int
    plan: str
    plan_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.EDITOR


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: int
    tenant_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Listing Schemas
class ListingBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    addr_line1: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    postal: Optional[str] = Field(None, max_length=20)
    country: str = Field("US", max_length=2)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    category_id: int
    tags: Optional[List[str]] = None
    hours_json: Optional[Dict[str, Any]] = None
    images_json: Optional[List[str]] = None


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    addr_line1: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    postal: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    hours_json: Optional[Dict[str, Any]] = None
    images_json: Optional[List[str]] = None


class ListingResponse(ListingBase):
    id: int
    tenant_id: int
    slug: str
    featured_until: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    tenant_id: int
    slug: str
    
    class Config:
        from_attributes = True


# Endorsement Schemas
class EndorsementBase(BaseModel):
    listing_id: int
    would_repeat: bool = True
    tags: Optional[List[str]] = None
    comment: Optional[str] = None


class EndorsementCreate(EndorsementBase):
    pass


class EndorsementResponse(EndorsementBase):
    id: int
    tenant_id: int
    user_id: Optional[int]
    txn_hash: str
    created_at: datetime
    ip_hash: str
    
    class Config:
        from_attributes = True


# Search Schemas
class SearchRequest(BaseModel):
    q: Optional[str] = None
    category: Optional[int] = None
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    radius_km: Optional[float] = Field(None, gt=0, le=1000)
    sort: Optional[str] = Field("relevance", pattern="^(relevance|distance|name|created)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class SearchResponse(BaseModel):
    listings: List[ListingResponse]
    total: int
    page: int
    limit: int
    has_next: bool


# Auth Schemas
class AuthRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    tenant_name: str = Field(..., min_length=1, max_length=200)
    tenant_slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")

class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    tenant: TenantResponse


# API Key Schemas
class ApiKeyResponse(BaseModel):
    api_key: str
    created_at: datetime


# Usage Schemas
class UsageResponse(BaseModel):
    tenant_id: int
    month: str
    api_calls: int
    listings_count: int
    members_count: int
    storage_mb: int


# Health Check Schema
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: bool
    redis: bool
    storage: bool


# Error Schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# Pagination Schema
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort: Optional[str] = None
    order: Optional[str] = Field("asc", pattern="^(asc|desc)$")