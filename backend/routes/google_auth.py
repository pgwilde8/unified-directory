"""
Google OAuth authentication routes for Business Directory
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
import httpx
from datetime import datetime, timedelta
from typing import Optional
import secrets

from database.database import get_db
from database.business_models import User
from backend.core.config import settings

router = APIRouter()


class GoogleUserInfo(BaseModel):
    """Google user information from OAuth"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: bool = False


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


@router.get("/google")
async def google_login():
    """Initiate Google OAuth login"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    
    # Google OAuth URL
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"state={state}"
    )
    
    # Store state in session/cookie for verification
    response = RedirectResponse(url=google_auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        max_age=600,  # 10 minutes
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax"
    )
    
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    # # Verify state parameter
    # stored_state = request.cookies.get("state")
    # if not state or state != stored_state:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f"Invalid state parameter {stored_state}"
    #     )
    
    try:
        # Exchange code for access token
        token_response = await _exchange_code_for_token(code)
        access_token = token_response["access_token"]
        
        # Get user info from Google
        user_info = await _get_google_user_info(access_token)
        
        # Create or update user in database
        user = await _create_or_update_user(db, user_info)
        
        # Generate JWT token
        jwt_token = _generate_jwt_token(user)
        
        # Clear OAuth state cookie
        response = RedirectResponse(url="/dashboard")
        response.delete_cookie("oauth_state")
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me")
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "profile_picture": user.profile_picture,
            "phone": user.phone,
            "is_verified": user.is_verified,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/logout")
async def logout():
    """Logout user"""
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    return response


async def _exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token"""
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        response.raise_for_status()
        return response.json()


async def _get_google_user_info(access_token: str) -> GoogleUserInfo:
    """Get user information from Google"""
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return GoogleUserInfo(
            id=data["id"],
            email=data["email"],
            name=data["name"],
            picture=data.get("picture"),
            verified_email=data.get("verified_email", False)
        )


async def _create_or_update_user(db: Session, user_info: GoogleUserInfo) -> User:
    """Create or update user in database"""
    # Check if user exists
    user = db.query(User).filter(User.google_id == user_info.id).first()
    
    if user:
        # Update existing user
        user.email = user_info.email
        user.name = user_info.name
        user.profile_picture = user_info.picture
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
    else:
        # Create new user
        user = User(
            google_id=user_info.id,
            email=user_info.email,
            name=user_info.name,
            profile_picture=user_info.picture,
            is_verified=user_info.verified_email,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    return user


def _generate_jwt_token(user: User) -> str:
    """Generate JWT token for user"""
    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "exp": expires_at,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(
        token_data, 
        settings.SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
