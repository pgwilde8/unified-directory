"""
FastAPI main application for White-label Multi-tenant Business Directory Platform
Following the master project specifications exactly
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
from backend.routes import tenant_api
from backend.middleware import TimingMiddleware, AuthMiddleware
from backend.core.config import settings

# Create FastAPI app for multi-tenant platform
app = FastAPI(
    title="White-label Business Directory Platform",
    description="Multi-tenant business directory platform with custom domains and white-label API",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourplatform.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(TimingMiddleware)
app.add_middleware(AuthMiddleware)

# Mount static files (only if directory exists)
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include tenant API router
app.include_router(tenant_api.router)

# Root endpoint - tenant resolution
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - resolve tenant and serve appropriate content"""
    # TODO: Implement tenant resolution based on domain/subdomain
    # For now, return a simple welcome page
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>White-label Business Directory Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .api-info { background: #f5f5f5; padding: 20px; border-radius: 8px; }
                .endpoint { margin: 10px 0; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏢 White-label Business Directory Platform</h1>
                    <p>Multi-tenant business directory platform with custom domains</p>
                </div>
                
                <div class="api-info">
                    <h2>API Endpoints</h2>
                    <div class="endpoint">POST /v1/auth/register - Register new tenant</div>
                    <div class="endpoint">POST /v1/auth/login - Login tenant owner</div>
                    <div class="endpoint">GET /v1/tenants/me - Get tenant info</div>
                    <div class="endpoint">POST /v1/listings - Create business listing</div>
                    <div class="endpoint">GET /v1/listings - Search listings</div>
                    <div class="endpoint">POST /v1/endorsements - Create endorsement</div>
                    <div class="endpoint">GET /v1/healthz - Health check</div>
                    
                    <p><a href="/api/docs">View API Documentation</a></p>
                </div>
            </div>
        </body>
        </html>
        """,
        status_code=200
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(pytz.timezone('US/Eastern')).isoformat(),
        "version": "1.0.0",
        "platform": "white-label-multi-tenant"
    }


@app.get("/api/stats")
async def get_stats(db=Depends(get_db)):
    """Get platform statistics"""
    from sqlalchemy import func
    from database.tenant_models import Tenant, User, Listing, Endorsement
    
    # Get basic counts
    total_tenants = db.query(Tenant).count()
    total_users = db.query(User).count()
    total_listings = db.query(Listing).count()
    total_endorsements = db.query(Endorsement).count()
    
    # Get active tenants
    active_tenants = db.query(Tenant).filter(Tenant.plan_status == "active").count()
    
    return {
        "total_tenants": total_tenants,
        "active_tenants": active_tenants,
        "total_users": total_users,
        "total_listings": total_listings,
        "total_endorsements": total_endorsements,
        "last_updated": datetime.now(pytz.timezone('US/Eastern')).isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main_tenant:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
