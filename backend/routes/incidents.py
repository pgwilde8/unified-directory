"""
Incidents API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import pytz

from database import get_db
from database.models import Incident, Source, Location
from backend.middleware import get_current_user
from backend.core.config import settings

router = APIRouter()


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: str
    source_name: str
    state: Optional[str]
    city: Optional[str]
    crime_type: str
    severity: str
    published_at: str
    discovered_at: str
    confidence_score: float


@router.get("/public", response_model=List[IncidentResponse])
async def get_public_incidents(
    limit: int = Query(50, le=100),
    state: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    hours: int = Query(24, le=168),  # Max 1 week
    db: Session = Depends(get_db)
):
    """Get recent incidents for public consumption"""
    
    # Calculate time filter
    eastern = pytz.timezone(settings.TIMEZONE)
    cutoff_time = datetime.now(eastern) - timedelta(hours=hours)
    
    # Build query - only show high and critical incidents on public dashboard
    query = db.query(Incident, Source).join(Source).filter(
        Incident.discovered_at >= cutoff_time,
        Incident.is_duplicate == False,
        Incident.severity.in_(["critical", "high"])
    )
    
    # Apply filters
    if state:
        query = query.filter(Incident.state == state.upper())
    
    if severity:
        query = query.filter(Incident.severity == severity)
    
    # Order by most recent first
    query = query.order_by(desc(Incident.published_at)).limit(limit)
    
    results = query.all()
    
    return [
        IncidentResponse(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            url=incident.url,
            source_name=source.name,
            state=incident.state,
            city=incident.city,
            crime_type=incident.crime_type,
            severity=incident.severity,
            published_at=incident.published_at.isoformat(),
            discovered_at=incident.discovered_at.isoformat(),
            confidence_score=incident.confidence_score
        )
        for incident, source in results
    ]


@router.get("/all", response_model=List[IncidentResponse])
async def get_all_incidents(
    limit: int = Query(100, le=500),
    state: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get all incidents for public consumption (including non-critical)"""
    
    # Calculate time filter
    eastern = pytz.timezone(settings.TIMEZONE)
    cutoff_time = datetime.now(eastern) - timedelta(hours=hours)
    
    # Build query - show all incidents
    query = db.query(Incident, Source).join(Source).filter(
        Incident.discovered_at >= cutoff_time,
        Incident.is_duplicate == False
    )
    
    # Apply filters
    if state:
        query = query.filter(Incident.state == state.upper())
    
    if severity:
        query = query.filter(Incident.severity == severity)
    
    # Order by most recent first
    query = query.order_by(desc(Incident.published_at)).limit(limit)
    
    results = query.all()
    
    return [
        IncidentResponse(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            url=incident.url,
            source_name=source.name,
            state=incident.state,
            city=incident.city,
            crime_type=incident.crime_type,
            severity=incident.severity,
            published_at=incident.published_at.isoformat(),
            discovered_at=incident.discovered_at.isoformat(),
            confidence_score=incident.confidence_score
        )
        for incident, source in results
    ]

@router.get("/admin", response_model=List[IncidentResponse])
async def get_admin_incidents(
    limit: int = Query(100, le=500),
    state: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    verified: Optional[bool] = Query(None),
    hours: int = Query(24, le=168),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get incidents for admin users (includes unverified)"""
    
    # Calculate time filter
    eastern = pytz.timezone(settings.TIMEZONE)
    cutoff_time = datetime.now(eastern) - timedelta(hours=hours)
    
    # Build query
    query = db.query(Incident, Source).join(Source).filter(
        Incident.discovered_at >= cutoff_time
    )
    
    # Apply filters
    if state:
        query = query.filter(Incident.state == state.upper())
    
    if severity:
        query = query.filter(Incident.severity == severity)
    
    if verified is not None:
        query = query.filter(Incident.is_verified == verified)
    
    # Order by most recent first
    query = query.order_by(desc(Incident.discovered_at)).limit(limit)
    
    results = query.all()
    
    return [
        IncidentResponse(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            url=incident.url,
            source_name=source.name,
            state=incident.state,
            city=incident.city,
            crime_type=incident.crime_type,
            severity=incident.severity,
            published_at=incident.published_at.isoformat(),
            discovered_at=incident.discovered_at.isoformat(),
            confidence_score=incident.confidence_score
        )
        for incident, source in results
    ]


@router.get("/stats")
async def get_incident_stats(
    hours: int = Query(24, le=168),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get incident statistics"""
    
    # Calculate time filter
    eastern = pytz.timezone(settings.TIMEZONE)
    cutoff_time = datetime.now(eastern) - timedelta(hours=hours)
    
    # Get counts by severity
    severity_counts = db.query(
        Incident.severity,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.discovered_at >= cutoff_time
    ).group_by(Incident.severity).all()
    
    # Get counts by state
    state_counts = db.query(
        Incident.state,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.discovered_at >= cutoff_time,
        Incident.state.isnot(None)
    ).group_by(Incident.state).order_by(
        func.count(Incident.id).desc()
    ).limit(10).all()
    
    # Get counts by crime type
    type_counts = db.query(
        Incident.crime_type,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.discovered_at >= cutoff_time
    ).group_by(Incident.crime_type).all()
    
    return {
        "time_period_hours": hours,
        "severity_breakdown": dict(severity_counts),
        "top_states": [{"state": state, "count": count} for state, count in state_counts],
        "crime_types": dict(type_counts),
        "generated_at": datetime.now(eastern).isoformat()
    }


@router.post("/verify/{incident_id}")
async def verify_incident(
    incident_id: int,
    verified: bool,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark incident as verified/unverified"""
    
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.is_verified = verified
    incident.processed_at = datetime.now(pytz.timezone(settings.TIMEZONE))
    
    db.commit()
    
    return {"message": f"Incident {incident_id} {'verified' if verified else 'unverified'}"}


@router.get("/states")
async def get_available_states(db: Session = Depends(get_db)):
    """Get list of available states with incident counts"""
    
    # Get states with incident counts from last 30 days
    cutoff_time = datetime.now(pytz.timezone(settings.TIMEZONE)) - timedelta(days=30)
    
    state_counts = db.query(
        Incident.state,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.discovered_at >= cutoff_time,
        Incident.state.isnot(None)
    ).group_by(Incident.state).order_by(Incident.state).all()
    
    return [
        {"state_code": state, "count": count}
        for state, count in state_counts
    ]
