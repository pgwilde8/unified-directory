"""
Clean multi-tenant models for white-label Business Directory Platform
Only includes the essential multi-tenant tables
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Tenant(Base):
    """Multi-tenant organization - exact spec from master project"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    domain = Column(String(255), unique=True, index=True)  # Custom domain
    logo_url = Column(String(500))
    theme = Column(JSON)  # Theme colors and branding
    plan = Column(String(50), default="free")  # free, premium, pro
    plan_status = Column(String(20), default="active")  # active, suspended, cancelled
    api_key_hash = Column(String(255), unique=True, index=True)  # Hashed API key
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    listings = relationship("Listing", back_populates="tenant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="tenant", cascade="all, delete-orphan")
    endorsements = relationship("Endorsement", back_populates="tenant", cascade="all, delete-orphan")
    moderation_reports = relationship("ModerationReport", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    usage_meters = relationship("UsageMeter", back_populates="tenant", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenants_slug_active', 'slug'),
        Index('idx_tenants_domain_active', 'domain'),
        Index('idx_tenants_plan_status', 'plan', 'plan_status'),
    )


class User(Base):
    """Users within tenants - exact spec from master project"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    pw_hash = Column(String(255), nullable=False)  # Password hash
    role = Column(String(20), default="member")  # owner, admin, editor
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    listings = relationship("Listing", back_populates="owner")
    endorsements = relationship("Endorsement", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="actor_user")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_tenant_email', 'tenant_id', 'email'),
        Index('idx_users_tenant_role', 'tenant_id', 'role'),
    )


class Listing(Base):
    """Business listings - exact spec from master project"""
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    website = Column(String(500))
    phone = Column(String(20))
    email = Column(String(255))
    
    # Address fields
    addr_line1 = Column(String(200))
    city = Column(String(100), index=True)
    region = Column(String(100), index=True)  # State/Province
    postal = Column(String(20), index=True)  # ZIP/Postal code
    country = Column(String(2), default="US", index=True)
    lat = Column(Float, index=True)  # Latitude for geo-search
    lng = Column(Float, index=True)  # Longitude for geo-search
    
    # Business details
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    tags = Column(JSON)  # Array of tags
    hours_json = Column(JSON)  # Business hours
    images_json = Column(JSON)  # Array of image URLs
    
    # Status and features
    featured_until = Column(DateTime)  # Premium feature
    status = Column(String(20), default="active")  # active, pending, suspended
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="listings")
    category = relationship("Category", back_populates="listings")
    owner = relationship("User", back_populates="listings")
    endorsements = relationship("Endorsement", back_populates="listing")
    
    # Indexes
    __table_args__ = (
        Index('idx_listings_tenant_category', 'tenant_id', 'category_id'),
        Index('idx_listings_tenant_city', 'tenant_id', 'city'),
        Index('idx_listings_tenant_status', 'tenant_id', 'status'),
        Index('idx_listings_tenant_slug', 'tenant_id', 'slug'),
        Index('idx_listings_geo', 'lat', 'lng'),
    )


class Category(Base):
    """Business categories - exact spec from master project"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    slug = Column(String(100), nullable=False, index=True)
    sort_order = Column(Integer, default=0)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="categories")
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category", back_populates="parent")
    listings = relationship("Listing", back_populates="category")
    
    # Indexes
    __table_args__ = (
        Index('idx_categories_tenant_parent', 'tenant_id', 'parent_id'),
        Index('idx_categories_tenant_slug', 'tenant_id', 'slug'),
        Index('idx_categories_tenant_sort', 'tenant_id', 'sort_order'),
    )


class Endorsement(Base):
    """Customer endorsements - exact spec from master project"""
    __tablename__ = "endorsements"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous
    would_repeat = Column(Boolean, default=True)
    tags = Column(JSON)  # Array of endorsement tags
    comment = Column(Text)
    txn_hash = Column(String(255), unique=True, index=True)  # Anti-spam transaction hash
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    ip_hash = Column(String(255), index=True)  # Hashed IP for anti-spam
    
    # Relationships
    tenant = relationship("Tenant", back_populates="endorsements")
    listing = relationship("Listing", back_populates="endorsements")
    user = relationship("User", back_populates="endorsements")
    
    # Indexes
    __table_args__ = (
        Index('idx_endorsements_tenant_listing', 'tenant_id', 'listing_id'),
        Index('idx_endorsements_tenant_created', 'tenant_id', 'created_at'),
        Index('idx_endorsements_txn_hash', 'txn_hash'),
    )


class ModerationReport(Base):
    """Moderation reports - exact spec from master project"""
    __tablename__ = "moderation_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    target_type = Column(String(50), nullable=False, index=True)  # listing, endorsement, user
    target_id = Column(Integer, nullable=False, index=True)
    reason_code = Column(String(50), nullable=False, index=True)
    evidence_urls = Column(JSON)  # Array of evidence URLs
    status = Column(String(20), default="pending")  # pending, approved, rejected
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    closed_at = Column(DateTime)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="moderation_reports")
    assignee = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_moderation_tenant_status', 'tenant_id', 'status'),
        Index('idx_moderation_tenant_type', 'tenant_id', 'target_type'),
        Index('idx_moderation_assigned', 'assigned_to', 'status'),
    )


class AuditLog(Base):
    """Audit logs - exact spec from master project"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    target_type = Column(String(50), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    meta_json = Column(JSON)  # Additional metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    actor_user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_tenant_action', 'tenant_id', 'action'),
        Index('idx_audit_tenant_created', 'tenant_id', 'created_at'),
        Index('idx_audit_actor_created', 'actor_user_id', 'created_at'),
    )


class UsageMeter(Base):
    """Usage meters - exact spec from master project"""
    __tablename__ = "usage_meters"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    month = Column(String(7), nullable=False, index=True)  # YYYY-MM format
    api_calls = Column(Integer, default=0)
    listings_count = Column(Integer, default=0)
    members_count = Column(Integer, default=0)
    storage_mb = Column(Integer, default=0)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="usage_meters")
    
    # Indexes
    __table_args__ = (
        Index('idx_usage_tenant_month', 'tenant_id', 'month'),
    )


class Member(Base):
    """Optional member model - exact spec from master project"""
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    plan = Column(String(50), default="basic")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant")
    
    # Indexes
    __table_args__ = (
        Index('idx_members_tenant_email', 'tenant_id', 'email'),
        Index('idx_members_tenant_status', 'tenant_id', 'status'),
    )
