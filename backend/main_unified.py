"""
Unified FastAPI application for Multi-tenant Business Directory Platform
Combines legacy Google OAuth functionality with multi-tenant API capabilities
Port: 9180 (Unified System)
"""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from datetime import datetime, timedelta
import pytz

from fastapi.templating import Jinja2Templates

from database.database import get_db
# Legacy routes (Google OAuth based)
from backend.routes import incidents, auth, admin, data_collection, google_auth, businesses, pages
# Multi-tenant routes (API key based)
from backend.routes import tenant_api
from backend.middleware import TimingMiddleware, AuthMiddleware
from backend.core.config import settings

# Create unified FastAPI app
app = FastAPI(
    title="Unified Business Directory Platform",
    description="Multi-tenant business directory platform with both Google OAuth and API key authentication",
    version="2.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middlewares
app.add_middleware(TimingMiddleware)
app.add_middleware(AuthMiddleware)

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception as e:
    print(f"Could not mount static files: {e}")

# Setup templates
try:
    templates = Jinja2Templates(directory="frontend")
except Exception as e:
    print(f"Could not setup templates: {e}")
    templates = None

# Include legacy routes (Google OAuth - port 9178 functionality)
app.include_router(incidents.router, prefix="/api", tags=["Incidents"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(data_collection.router, prefix="/api/data", tags=["Data Collection"])
app.include_router(google_auth.router, prefix="/api/auth", tags=["Google Auth"])
app.include_router(businesses.router, prefix="/api", tags=["Businesses"])
app.include_router(pages.router, tags=["Pages"])

# Include multi-tenant routes (API key based - port 9179 functionality)
app.include_router(tenant_api.router, prefix="/v1", tags=["Multi-Tenant API"])

@app.get("/")
async def root():
    """Root endpoint showing unified system info"""
    return {
        "message": "Unified Business Directory Platform",
        "version": "2.0.0",
        "features": {
            "legacy_auth": "Google OAuth integration",
            "multi_tenant": "API key based multi-tenancy",
            "database": "PostgreSQL with tenant isolation",
            "port": 9180
        },
        "endpoints": {
            "legacy": {
                "auth": "/api/auth",
                "businesses": "/api/businesses", 
                "admin": "/api/admin",
                "docs": "/api/docs"
            },
            "multi_tenant": {
                "auth": "/v1/auth",
                "listings": "/v1/listings",
                "endorsements": "/v1/endorsements",
                "usage": "/v1/usage"
            }
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "system": "unified",
        "port": 9180
    }

@app.get("/info")
async def system_info():
    """System information endpoint"""
    return {
        "system": "Unified Business Directory Platform",
        "version": "2.0.0", 
        "port": 9180,
        "authentication": ["Google OAuth", "API Keys"],
        "features": [
            "Business listings",
            "Multi-tenant isolation",
            "File uploads",
            "Endorsements",
            "Usage tracking",
            "Stripe integration"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "backend.main_unified:app",
        host="0.0.0.0",
        port=9180,
        reload=True
    )