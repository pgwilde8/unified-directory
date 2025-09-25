"""
Custom middleware for authentication and timing controls
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import jwt
import pytz
from datetime import datetime, timezone
from backend.core.config import settings

security = HTTPBearer()


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce login time restrictions"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip timing checks for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Check if current time is within allowed login hours
        if not self._is_login_time_allowed():
            return Response(
                content='{"error": "Access denied: System only available during business hours (6 AM - 10 PM EST)"}',
                status_code=403,
                media_type="application/json"
            )
        
        return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no timing restrictions)"""
        public_paths = [
            "/",
            "/api/health",
            "/api/stats",
            "/api/incidents/public",
            "/static/",
            "/api/docs",
            "/api/redoc"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _is_login_time_allowed(self) -> bool:
        """Check if current time is within allowed login hours"""
        # Get current time in Eastern timezone
        eastern = pytz.timezone(settings.TIMEZONE)
        current_time = datetime.now(eastern)
        current_hour = current_time.hour
        
        # Check if within allowed hours (6 AM to 10 PM)
        return settings.LOGIN_START_HOUR <= current_hour <= settings.LOGIN_END_HOUR


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication"""
    
    async def dispatch(self, request: Request, call_next):
        # Add request timing
        start_time = time.time()
        
        response = await call_next(request)
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_admin_access(current_user: str = Depends(get_current_user)):
    """Verify user has admin access"""
    if current_user != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
