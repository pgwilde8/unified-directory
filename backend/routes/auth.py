"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import jwt
import pytz
from datetime import datetime, timedelta
from backend.core.config import settings

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str
    login_time_allowed: bool


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return JWT token"""
    
    # Check if login time is allowed
    login_time_allowed = _is_login_time_allowed()
    
    # Verify credentials
    if (login_data.username == settings.ADMIN_USERNAME and 
        login_data.password == settings.ADMIN_PASSWORD):
        
        # Create JWT token
        expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_TIMEOUT_HOURS)
        token_data = {
            "sub": login_data.username,
            "exp": expires_at,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            expires_at=expires_at.isoformat(),
            login_time_allowed=login_time_allowed
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )


@router.get("/status")
async def auth_status():
    """Get authentication status and timing info"""
    eastern = pytz.timezone(settings.TIMEZONE)
    current_time = datetime.now(eastern)
    
    return {
        "current_time": current_time.isoformat(),
        "timezone": settings.TIMEZONE,
        "login_allowed": _is_login_time_allowed(),
        "login_hours": f"{settings.LOGIN_START_HOUR}:00 - {settings.LOGIN_END_HOUR}:00",
        "next_login_time": _get_next_login_time()
    }


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Logged out successfully"}


def _is_login_time_allowed() -> bool:
    """Check if current time is within allowed login hours"""
    eastern = pytz.timezone(settings.TIMEZONE)
    current_time = datetime.now(eastern)
    current_hour = current_time.hour
    
    return settings.LOGIN_START_HOUR <= current_hour <= settings.LOGIN_END_HOUR


def _get_next_login_time() -> str:
    """Get next allowed login time"""
    eastern = pytz.timezone(settings.TIMEZONE)
    current_time = datetime.now(eastern)
    
    if _is_login_time_allowed():
        return "Now"
    
    # If before login hours, next login is today at LOGIN_START_HOUR
    if current_time.hour < settings.LOGIN_START_HOUR:
        next_login = current_time.replace(
            hour=settings.LOGIN_START_HOUR, 
            minute=0, 
            second=0, 
            microsecond=0
        )
    else:
        # If after hours, next login is tomorrow at LOGIN_START_HOUR
        next_login = current_time.replace(
            hour=settings.LOGIN_START_HOUR, 
            minute=0, 
            second=0, 
            microsecond=0
        ) + timedelta(days=1)
    
    return next_login.isoformat()
