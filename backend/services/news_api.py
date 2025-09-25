"""
NewsAPI service for collecting violent crime incidents
"""
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from database import get_db
from database.models import Incident, Source, ApiLog
import pytz
from backend.core.config import settings

logger = logging.getLogger(__name__)

class NewsAPIService:
    """Service for collecting crime data from NewsAPI"""
    
    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY or "d7a060516f7a43fa9638b44b6c570dbc"
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            "X-Api-Key": self.api_key
        }
        
        # Crime keywords for filtering
        self.crime_keywords = [
            "shooting", "homicide", "murder", "violent crime", "stabbing", 
            "assault", "robbery", "domestic violence", "mass shooting",
            "school shooting", "gun violence", "knife attack", "beating",
            "killed", "fatal", "dead", "victim", "suspect", "arrest"
        ]
        
        # Keywords to exclude (false positives)
        self.exclude_keywords = [
            "video game", "movie", "film", "book", "novel", "fiction",
            "game", "sports", "entertainment", "review", "trailer"
        ]
    
    def build_search_query(self) -> str:
        """Build the search query for crime-related articles"""
        # Focus on significant violent crimes only
        significant_crimes = [
            "shooting", "homicide", "murder", "mass shooting", 
            "school shooting", "gun violence", "fatal", "killed",
            "stabbing", "violent crime", "assault", "robbery"
        ]
        return " OR ".join(significant_crimes)
    
    def collect_incidents(self, db: Session, hours_back: int = 24) -> Dict:
        """Collect recent crime incidents from NewsAPI"""
        start_time = datetime.now()
        errors = []
        articles_found = 0
        articles_processed = 0
        
        try:
            # Calculate date range
            eastern = pytz.timezone('US/Eastern')
            now = datetime.now(eastern)
            from_date = now - timedelta(hours=hours_back)
            
            # Build search parameters (remove date restrictions for now)
            params = {
                "q": self.build_search_query(),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 100
            }
            
            # Make API request
            logger.info(f"Making NewsAPI request with params: {params}")
            response = requests.get(
                f"{self.base_url}/everything",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info(f"NewsAPI response status: {response.status_code}")
            logger.info(f"NewsAPI response text: {response.text[:500]}")
            
            if response.status_code != 200:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                errors.append(error_msg)
                
                # Log API error
                self._log_api_call(
                    db, "everything", str(params), response.status_code,
                    response_time, 0, 0, error_msg
                )
                
                return {
                    "success": False,
                    "articles_found": 0,
                    "articles_processed": 0,
                    "errors": errors
                }
            
            data = response.json()
            articles = data.get("articles", [])
            articles_found = len(articles)
            
            # Process articles
            for article in articles:
                try:
                    if self._process_article(db, article):
                        articles_processed += 1
                except Exception as e:
                    error_msg = f"Error processing article: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Log successful API call
            self._log_api_call(
                db, "everything", str(params), response.status_code,
                response_time, articles_found, articles_processed, None
            )
            
            return {
                "success": True,
                "articles_found": articles_found,
                "articles_processed": articles_processed,
                "errors": errors
            }
            
        except Exception as e:
            error_msg = f"Unexpected error in collect_incidents: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Log error
            self._log_api_call(
                db, "everything", str(params), 500,
                response_time, 0, 0, error_msg
            )
            
            return {
                "success": False,
                "articles_found": 0,
                "articles_processed": 0,
                "errors": errors
            }
    
    def _process_article(self, db: Session, article: Dict) -> bool:
        """Process a single article and create incident if relevant"""
        try:
            # Extract article data
            title = article.get("title", "")
            description = article.get("description", "")
            url = article.get("url", "")
            source_name = article.get("source", {}).get("name", "Unknown")
            published_at = article.get("publishedAt", "")
            
            # Skip if missing essential data
            if not title or not url or not published_at:
                return False
            
            # Check if already exists
            existing = db.query(Incident).filter(Incident.url == url).first()
            if existing:
                return False
            
            # Get or create source
            source = self._get_or_create_source(db, source_name)
            
            # Classify the incident
            classification = self._classify_incident(title, description)
            
            # Skip filtered out incidents
            if classification["type"] == "filtered_out":
                return False
            
            # Extract location
            location = self._extract_location(title, description)
            
            # Create incident
            incident = Incident(
                title=title,
                description=description,
                url=url,
                source_id=source.id,
                state=location.get("state"),
                city=location.get("city"),
                location_text=location.get("text"),
                crime_type=classification["type"],
                severity=classification["severity"],
                published_at=datetime.fromisoformat(published_at.replace('Z', '+00:00')),
                confidence_score=classification["confidence"],
                is_verified=False,
                is_duplicate=False
            )
            
            db.add(incident)
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing article {article.get('url', 'unknown')}: {str(e)}")
            db.rollback()
            return False
    
    def _get_or_create_source(self, db: Session, source_name: str) -> Source:
        """Get existing source or create new one"""
        source = db.query(Source).filter(Source.name == source_name).first()
        
        if not source:
            # Create new source with default reliability score
            source = Source(
                name=source_name,
                domain=self._extract_domain(source_name),
                reliability_score=0.5
            )
            db.add(source)
            db.commit()
            db.refresh(source)
        
        return source
    
    def _extract_domain(self, source_name: str) -> str:
        """Extract domain from source name"""
        # Simple domain extraction - you might want to improve this
        domain_mapping = {
            "CNN": "cnn.com",
            "Fox News": "foxnews.com",
            "ABC News": "abcnews.go.com",
            "CBS News": "cbsnews.com",
            "NBC News": "nbcnews.com",
            "Associated Press": "apnews.com",
            "Reuters": "reuters.com",
            "USA Today": "usatoday.com"
        }
        
        return domain_mapping.get(source_name, f"{source_name.lower().replace(' ', '')}.com")
    
    def _classify_incident(self, title: str, description: str) -> Dict:
        """Classify incident type and severity - focus on significant violent crimes"""
        text = f"{title} {description}".lower()
        
        # Filter out entertainment content first
        entertainment_keywords = [
            "movie", "film", "dvd", "blu-ray", "streaming", "netflix", "hulu", "amazon prime",
            "imdb", "rating", "genre", "drama", "comedy", "action", "thriller", "horror",
            "plot", "synopsis", "cast", "director", "producer", "awards", "nominations",
            "trailer", "review", "critic", "box office", "theater", "cinema", "premiere",
            "sequel", "remake", "adaptation", "based on", "inspired by", "fictional",
            "character", "actor", "actress", "starring", "featuring", "performance",
            "amzn", "web-dl", "h264", "1080p", "720p", "4k", "uhd", "torrent", "download"
        ]
        
        # Check if this is entertainment content
        for keyword in entertainment_keywords:
            if keyword in text:
                return {"type": "filtered_out", "severity": "filtered", "confidence": 0.0}
        
        # Enhanced classification rules for significant violent crimes only
        classifications = {
            "mass_violence": {
                "keywords": ["mass shooting", "mass casualty", "multiple victims", "rampage", "mass murder"],
                "severity": "critical",
                "min_confidence": 0.3
            },
            "school_incident": {
                "keywords": ["school shooting", "school", "campus", "student", "teacher", "education"],
                "severity": "critical",
                "min_confidence": 0.3
            },
            "homicide": {
                "keywords": ["homicide", "murder", "killed", "death", "dead", "fatal", "slain"],
                "severity": "high",
                "min_confidence": 0.4
            },
            "shooting": {
                "keywords": ["shooting", "shot", "gun", "firearm", "gunman", "gunshot"],
                "severity": "medium",
                "min_confidence": 0.5
            },
            "stabbing": {
                "keywords": ["stabbing", "stabbed", "knife", "cut", "slashed"],
                "severity": "medium",
                "min_confidence": 0.5
            }
        }
        
        # Find best match with minimum confidence threshold
        best_match = {"type": "other", "severity": "low", "confidence": 0.0}
        
        for crime_type, config in classifications.items():
            keyword_count = sum(1 for keyword in config["keywords"] if keyword in text)
            confidence = min(keyword_count / len(config["keywords"]), 1.0)
            min_confidence = config.get("min_confidence", 0.3)
            
            # Only classify if confidence meets minimum threshold
            if confidence >= min_confidence and confidence > best_match["confidence"]:
                best_match = {
                    "type": crime_type,
                    "severity": config["severity"],
                    "confidence": confidence
                }
        
        # Filter out low-confidence incidents
        if best_match["confidence"] < 0.3:
            return {"type": "filtered_out", "severity": "filtered", "confidence": 0.0}
        
        return best_match
    
    def _extract_location(self, title: str, description: str) -> Dict:
        """Extract location information from text"""
        text = f"{title} {description}"
        
        # US state abbreviations
        states = {
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        }
        
        # Find state mentions
        for state in states:
            if f" {state} " in text or text.endswith(f" {state}") or text.startswith(f"{state} "):
                return {"state": state, "city": None, "text": None}
        
        return {"state": None, "city": None, "text": None}
    
    def _log_api_call(self, db: Session, endpoint: str, query: str, 
                     status_code: int, response_time: int, 
                     articles_found: int, articles_processed: int, 
                     errors: Optional[str]):
        """Log API call to database"""
        try:
            api_log = ApiLog(
                endpoint=endpoint,
                query=query,
                status_code=status_code,
                response_time_ms=response_time,
                articles_found=articles_found,
                articles_processed=articles_processed,
                errors=errors
            )
            db.add(api_log)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging API call: {str(e)}")
    
    def get_preferred_domains(self) -> str:
        """Get comma-separated list of preferred news domains"""
        return "cnn.com,foxnews.com,abcnews.go.com,cbsnews.com,nbcnews.com,apnews.com,reuters.com,usatoday.com,washingtonpost.com,nytimes.com"
