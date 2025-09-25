"""
FastAPI main application for Directorys
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
from backend.routes import incidents, auth, admin, data_collection, google_auth, businesses,pages
from backend.middleware import TimingMiddleware, AuthMiddleware
from backend.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Business Directory API",
    description="Business Directory management system with Google OAuth authentication",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(TimingMiddleware)
app.add_middleware(AuthMiddleware)

# Mount static files (only if directory exists)
import os
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(google_auth.router, prefix="/api/auth", tags=["google-auth"])
app.include_router(businesses.router, prefix="/api/businesses", tags=["businesses"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(data_collection.router, prefix="/api/data", tags=["data-collection"])
app.include_router(pages.router)

# @app.get("/", response_class=HTMLResponse)
# async def root():
#     """Serve the main public dashboard"""
#     try:
#         with open("frontend/login.html", "r" , encoding="utf-8") as f:
#             return HTMLResponse(content=f.read())
#     except FileNotFoundError:
#         return HTMLResponse(
#             content="<h1>Business Directory</h1><p>Welcome to our business directory!</p>",
#             status_code=200
#         )


# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard():
#     """Serve the business owner dashboard"""
#     try:
#         with open("frontend/dashboard.html", "r" , encoding="utf-8") as f:
#             return HTMLResponse(content=f.read())
#     except FileNotFoundError:
#         return HTMLResponse(
#             content="<h1>Dashboard</h1><p>Dashboard coming soon...</p>",
#             status_code=200
#         )

# @app.get("/admin.html", response_class=HTMLResponse)
# async def admin_dashboard():
#     """Serve the admin dashboard"""
#     try:
#         with open("frontend/admin.html", "r", encoding="utf-8") as f:
#             return HTMLResponse(content=f.read())
#     except FileNotFoundError:
#         return HTMLResponse(
#             content="<h1>Admin Dashboard</h1><p>Admin panel coming soon...</p>",
#             status_code=200
#         )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(pytz.timezone('US/Eastern')).isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/stats")
async def get_stats(db=Depends(get_db)):
    """Get system statistics"""
    from sqlalchemy import func
    from database.models import Incident, Source
    
    # Get basic counts
    total_incidents = db.query(Incident).count()
    active_sources = db.query(Source).filter(Source.is_active == True).count()
    
    # Get incidents from last 24 hours
    yesterday = datetime.now(pytz.timezone('US/Eastern')) - timedelta(days=1)
    recent_incidents = db.query(Incident).filter(
        Incident.discovered_at >= yesterday
    ).count()
    
    return {
        "total_incidents": total_incidents,
        "active_sources": active_sources,
        "recent_incidents_24h": recent_incidents,
        "last_updated": datetime.now(pytz.timezone('US/Eastern')).isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
