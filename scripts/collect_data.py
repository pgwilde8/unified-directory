#!/usr/bin/env python3
"""
Scheduled data collection script for Directory
"""
import os
import sys
import logging
from datetime import datetime
import pytz

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from backend.services.news_api import NewsAPIService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/webwise/directory/logs/data_collection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def collect_crime_data():
    """Collect crime data from NewsAPI"""
    db = SessionLocal()
    
    try:
        logger.info("Starting scheduled data collection")
        
        # Create NewsAPI service
        news_service = NewsAPIService()
        
        # Collect incidents from last 2 hours (overlap for safety)
        result = news_service.collect_incidents(db, hours_back=2)
        
        if result["success"]:
            logger.info(f"Data collection successful: {result['articles_processed']} incidents processed")
        else:
            logger.error(f"Data collection failed: {result['errors']}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error in scheduled data collection: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()

if __name__ == "__main__":
    # Log start time
    eastern = pytz.timezone('US/Eastern')
    start_time = datetime.now(eastern)
    logger.info(f"Data collection started at {start_time.isoformat()}")
    
    # Run collection
    result = collect_crime_data()
    
    # Log completion
    end_time = datetime.now(eastern)
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Data collection completed at {end_time.isoformat()} (took {duration:.2f} seconds)")
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)
