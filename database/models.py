"""
Database models for Directory system
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

# Import business models to make them available for Alembic
from database.business_models import *

# Import tenant models for multi-tenancy
from database.tenant_models import *


class SeverityLevel(enum.Enum):
    """Crime severity levels"""
    LOW = "low"          # Assaults, minor incidents
    MEDIUM = "medium"    # Shootings, stabbings
    HIGH = "high"        # Homicides, mass shootings
    CRITICAL = "critical"  # School shootings, terrorist acts


class CrimeType(enum.Enum):
    """Crime type categories"""
    SHOOTING = "shooting"
    HOMICIDE = "homicide"
    ASSAULT = "assault"
    STABBING = "stabbing"
    ROBBERY = "robbery"
    DOMESTIC_VIOLENCE = "domestic_violence"
    MASS_VIOLENCE = "mass_violence"
    SCHOOL_INCIDENT = "school_incident"
    OTHER = "other"


class Incident(Base):
    """Main incidents table"""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    url = Column(String(1000), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    
    # Location data
    state = Column(String(2), index=True)  # US state abbreviation
    city = Column(String(100), index=True)
    location_text = Column(String(200))  # Raw location from article
    
    # Classification
    crime_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    
    # Timestamps
    published_at = Column(DateTime, nullable=False, index=True)
    discovered_at = Column(DateTime, server_default=func.now(), nullable=False)
    processed_at = Column(DateTime, server_default=func.now())
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)  # AI confidence in classification
    
    # Relationships
    source = relationship("Source", back_populates="incidents")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_incidents_state_time', 'state', 'published_at'),
        Index('idx_incidents_severity_time', 'severity', 'published_at'),
        Index('idx_incidents_type_time', 'crime_type', 'published_at'),
    )


class Source(Base):
    """News sources with reliability scores"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    domain = Column(String(100), nullable=False, unique=True)
    reliability_score = Column(Float, default=0.5)  # 0.0 to 1.0
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    incidents = relationship("Incident", back_populates="source")


class Location(Base):
    """US states and major cities for filtering"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    state_code = Column(String(2), nullable=False, index=True)
    state_name = Column(String(50), nullable=False)
    city = Column(String(100), nullable=True, index=True)
    is_major_city = Column(Boolean, default=False)
    population = Column(Integer, nullable=True)  # For sorting by city size


class ApiLog(Base):
    """Track NewsAPI calls and performance"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False)
    query = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    articles_found = Column(Integer, default=0)
    articles_processed = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)


class IncidentCategory(Base):
    """Crime type definitions and keywords"""
    __tablename__ = "incident_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    keywords = Column(Text, nullable=False)  # JSON array of keywords
    severity_level = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class SystemStats(Base):
    """Daily system statistics"""
    __tablename__ = "system_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    total_incidents = Column(Integer, default=0)
    incidents_by_state = Column(Text)  # JSON object
    incidents_by_type = Column(Text)   # JSON object
    incidents_by_severity = Column(Text)  # JSON object
    api_calls_made = Column(Integer, default=0)
    api_errors = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

