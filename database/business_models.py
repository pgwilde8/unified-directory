"""
Database models for Business Directory system
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class BusinessCategory(enum.Enum):
    """Business category types"""
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    SERVICE = "service"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    AUTOMOTIVE = "automotive"
    PROFESSIONAL = "professional"
    OTHER = "other"


class User(Base):
    """Business owner users (legacy single-tenant)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    profile_picture = Column(String(500))  # URL to profile picture
    phone = Column(String(20))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_login = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    businesses = relationship("Business", back_populates="owner", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_google_id', 'google_id'),
    )


class Business(Base):
    """Business listings"""
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic business info
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), nullable=False, index=True)
    
    # Contact information
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(500))
    
    # Location
    address = Column(String(300))
    city = Column(String(100), index=True)
    state = Column(String(2), index=True)
    zip_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Business details
    hours = Column(JSON)  # Store business hours as JSON
    price_range = Column(String(10))  # $, $$, $$$, $$$$
    amenities = Column(JSON)  # Array of amenities
    tags = Column(JSON)  # Array of tags for search
    
    # Images and files
    logo_url = Column(String(500))
    images = Column(JSON)  # Array of image URLs
    documents = Column(JSON)  # Array of document URLs
    
    # Status and approval
    is_approved = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # SEO and search
    slug = Column(String(200), unique=True, index=True)
    meta_description = Column(String(300))
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime)
    
    # Relationships
    owner = relationship("User", back_populates="businesses")
    reviews = relationship("BusinessReview", back_populates="business", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_businesses_category_city', 'category', 'city'),
        Index('idx_businesses_state_city', 'state', 'city'),
        Index('idx_businesses_approved_active', 'is_approved', 'is_active'),
        Index('idx_businesses_owner_approved', 'owner_id', 'is_approved'),
        Index('idx_businesses_featured', 'is_featured', 'is_approved', 'is_active'),
    )


class BusinessReview(Base):
    """Customer reviews for businesses"""
    __tablename__ = "business_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Reviewer info (can be anonymous)
    reviewer_name = Column(String(100))
    reviewer_email = Column(String(255))
    reviewer_phone = Column(String(20))
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200))
    content = Column(Text)
    
    # Review status
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="reviews")
    
    # Indexes
    __table_args__ = (
        Index('idx_reviews_business_rating', 'business_id', 'rating'),
        Index('idx_reviews_business_approved', 'business_id', 'is_approved'),
    )


class BusinessClaim(Base):
    """Business ownership claims"""
    __tablename__ = "business_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Claim details
    claim_reason = Column(Text)
    supporting_documents = Column(JSON)  # Array of document URLs
    
    # Status
    status = Column(String(20), default="pending")  # pending, approved, rejected
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    review_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime)
    
    # Relationships
    business = relationship("Business")
    claimant = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_claims_business_status', 'business_id', 'status'),
        Index('idx_claims_user_status', 'user_id', 'status'),
    )


class BusinessAnalytics(Base):
    """Business analytics and metrics"""
    __tablename__ = "business_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    
    # Metrics
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    phone_calls = Column(Integer, default=0)
    website_visits = Column(Integer, default=0)
    direction_requests = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    business = relationship("Business")
    
    # Indexes
    __table_args__ = (
        Index('idx_analytics_business_date', 'business_id', 'date'),
    )


class SystemSettings(Base):
    """System-wide settings and configuration"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(String(300))
    is_public = Column(Boolean, default=False)  # Can be accessed without auth
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_settings_key_public', 'key', 'is_public'),
    )
