"""
Admin routes for system management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import pytz

from database import get_db
from database.models import Incident, Source, ApiLog, SystemStats
from backend.middleware import verify_admin_access
from backend.core.config import settings

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    current_user: str = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Admin dashboard data"""
    
    eastern = pytz.timezone(settings.TIMEZONE)
    now = datetime.now(eastern)
    
    # Get counts
    total_incidents = db.query(Incident).count()
    verified_incidents = db.query(Incident).filter(Incident.is_verified == True).count()
    unverified_incidents = total_incidents - verified_incidents
    
    # Get today's incidents
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_incidents = db.query(Incident).filter(
        Incident.discovered_at >= today_start
    ).count()
    
    # Get incidents by severity
    severity_counts = db.query(
        Incident.severity,
        func.count(Incident.id).label('count')
    ).group_by(Incident.severity).all()
    
    # Get recent API logs
    recent_logs = db.query(ApiLog).order_by(
        ApiLog.created_at.desc()
    ).limit(10).all()
    
    # Get system stats
    system_stats = db.query(SystemStats).order_by(
        SystemStats.date.desc()
    ).limit(7).all()
    
    return {
        "summary": {
            "total_incidents": total_incidents,
            "verified_incidents": verified_incidents,
            "unverified_incidents": unverified_incidents,
            "today_incidents": today_incidents
        },
        "severity_breakdown": dict(severity_counts),
        "recent_api_logs": [
            {
                "id": log.id,
                "endpoint": log.endpoint,
                "status_code": log.status_code,
                "response_time_ms": log.response_time_ms,
                "articles_found": log.articles_found,
                "created_at": log.created_at.isoformat()
            }
            for log in recent_logs
        ],
        "system_stats": [
            {
                "date": stat.date.isoformat(),
                "total_incidents": stat.total_incidents,
                "api_calls_made": stat.api_calls_made,
                "api_errors": stat.api_errors
            }
            for stat in system_stats
        ],
        "current_time": now.isoformat(),
        "login_time_allowed": _is_login_time_allowed()
    }


@router.get("/sources")
async def get_sources(
    current_user: str = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get news sources with statistics"""
    
    sources = db.query(Source).all()
    
    source_stats = []
    for source in sources:
        # Get incident count for this source
        incident_count = db.query(Incident).filter(
            Incident.source_id == source.id
        ).count()
        
        # Get recent incident count (last 7 days)
        cutoff = datetime.now(pytz.timezone(settings.TIMEZONE)) - timedelta(days=7)
        recent_count = db.query(Incident).filter(
            Incident.source_id == source.id,
            Incident.discovered_at >= cutoff
        ).count()
        
        source_stats.append({
            "id": source.id,
            "name": source.name,
            "domain": source.domain,
            "reliability_score": source.reliability_score,
            "is_active": source.is_active,
            "total_incidents": incident_count,
            "recent_incidents_7d": recent_count,
            "created_at": source.created_at.isoformat()
        })
    
    return source_stats


@router.post("/sources/{source_id}/toggle")
async def toggle_source(
    source_id: int,
    current_user: str = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Toggle source active status"""
    
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    source.is_active = not source.is_active
    db.commit()
    
    return {
        "message": f"Source {source.name} {'activated' if source.is_active else 'deactivated'}",
        "is_active": source.is_active
    }


@router.get("/api-logs")
async def get_api_logs(
    limit: int = 100,
    current_user: str = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get API logs"""
    
    logs = db.query(ApiLog).order_by(
        ApiLog.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "endpoint": log.endpoint,
            "query": log.query,
            "status_code": log.status_code,
            "response_time_ms": log.response_time_ms,
            "articles_found": log.articles_found,
            "articles_processed": log.articles_processed,
            "errors": log.errors,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]


@router.get("/system-health")
async def system_health(
    current_user: str = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """System health check"""
    
    eastern = pytz.timezone(settings.TIMEZONE)
    now = datetime.now(eastern)
    
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check recent API activity
    recent_logs = db.query(ApiLog).filter(
        ApiLog.created_at >= now - timedelta(hours=1)
    ).count()
    
    # Check for recent errors
    recent_errors = db.query(ApiLog).filter(
        ApiLog.created_at >= now - timedelta(hours=1),
        ApiLog.status_code >= 400
    ).count()
    
    return {
        "timestamp": now.isoformat(),
        "database": db_status,
        "recent_api_calls_1h": recent_logs,
        "recent_errors_1h": recent_errors,
        "login_time_allowed": _is_login_time_allowed(),
        "timezone": settings.TIMEZONE
    }


def _is_login_time_allowed() -> bool:
    """Check if current time is within allowed login hours"""
    eastern = pytz.timezone(settings.TIMEZONE)
    current_time = datetime.now(eastern)
    current_hour = current_time.hour
    
    return settings.LOGIN_START_HOUR <= current_hour <= settings.LOGIN_END_HOUR
