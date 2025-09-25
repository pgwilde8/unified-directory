"""
Data collection routes for NewsAPI integration
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
import logging

from database import get_db
from backend.services.news_api import NewsAPIService
from backend.middleware import verify_admin_access

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/collect-news")
async def collect_news_data(
    hours_back: int = 24,
    current_user: str = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Trigger news data collection from NewsAPI"""
    try:
        logger.info(f"Starting data collection for {hours_back} hours")
        news_service = NewsAPIService()
        
        # Run synchronously to see errors
        result = run_data_collection(db, news_service, hours_back)
        logger.info(f"Data collection result: {result}")
        return result
            
    except Exception as e:
        logger.error(f"Error starting data collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting data collection: {str(e)}")

@router.get("/collection-status")
async def get_collection_status(
    current_user: str = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get the status of data collection"""
    try:
        from sqlalchemy import func, desc
        from database.models import ApiLog, Incident
        
        # Get latest API log
        latest_log = db.query(ApiLog).order_by(desc(ApiLog.created_at)).first()
        
        # Get recent incidents count
        from datetime import datetime, timedelta
        import pytz
        
        eastern = pytz.timezone('US/Eastern')
        last_hour = datetime.now(eastern) - timedelta(hours=1)
        
        recent_incidents = db.query(Incident).filter(
            Incident.discovered_at >= last_hour
        ).count()
        
        return {
            "latest_collection": {
                "timestamp": latest_log.created_at.isoformat() if latest_log else None,
                "articles_found": latest_log.articles_found if latest_log else 0,
                "articles_processed": latest_log.articles_processed if latest_log else 0,
                "status_code": latest_log.status_code if latest_log else None,
                "errors": latest_log.errors if latest_log else None
            },
            "recent_incidents_last_hour": recent_incidents,
            "collection_active": latest_log is not None and latest_log.status_code == 200
        }
        
    except Exception as e:
        logger.error(f"Error getting collection status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting collection status: {str(e)}")

@router.get("/test-newsapi")
async def test_newsapi_connection():
    """Test NewsAPI connection and search"""
    try:
        import requests
        from backend.core.config import settings
        
        # Test basic API connection
        headers = {"X-Api-Key": settings.NEWSAPI_KEY}
        
        # Simple test query
        params = {
            "q": "shooting",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }
        
        response = requests.get(
            "https://newsapi.org/v2/everything",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            return {
                "status": "success",
                "message": "NewsAPI connection successful",
                "articles_found": len(articles),
                "sample_articles": [
                    {
                        "title": article.get("title", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "published": article.get("publishedAt", "")
                    }
                    for article in articles[:3]
                ]
            }
        else:
            return {
                "status": "error",
                "message": f"NewsAPI request failed: {response.status_code}",
                "response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error testing NewsAPI: {str(e)}")
        return {
            "status": "error",
            "message": f"Error testing NewsAPI: {str(e)}"
        }

def run_data_collection(db: Session, news_service: NewsAPIService, hours_back: int) -> Dict:
    """Run the actual data collection"""
    try:
        logger.info(f"Starting data collection for last {hours_back} hours")
        
        result = news_service.collect_incidents(db, hours_back)
        
        logger.info(f"Data collection completed: {result}")
        
        return {
            "message": "Data collection completed",
            "hours_back": hours_back,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")
        return {
            "message": "Data collection failed",
            "error": str(e),
            "hours_back": hours_back
        }
