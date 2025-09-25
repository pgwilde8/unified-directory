"""
Initialize database with seed data
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from database.models import Source, Location, IncidentCategory, SeverityLevel, CrimeType


def create_initial_sources(db: Session):
    """Create initial news sources with reliability scores"""
    sources_data = [
        {"name": "CNN", "domain": "cnn.com", "reliability_score": 0.9},
        {"name": "Fox News", "domain": "foxnews.com", "reliability_score": 0.85},
        {"name": "ABC News", "domain": "abcnews.go.com", "reliability_score": 0.9},
        {"name": "CBS News", "domain": "cbsnews.com", "reliability_score": 0.9},
        {"name": "NBC News", "domain": "nbcnews.com", "reliability_score": 0.9},
        {"name": "Associated Press", "domain": "apnews.com", "reliability_score": 0.95},
        {"name": "Reuters", "domain": "reuters.com", "reliability_score": 0.95},
        {"name": "USA Today", "domain": "usatoday.com", "reliability_score": 0.85},
        {"name": "Washington Post", "domain": "washingtonpost.com", "reliability_score": 0.9},
        {"name": "New York Times", "domain": "nytimes.com", "reliability_score": 0.9},
        {"name": "Los Angeles Times", "domain": "latimes.com", "reliability_score": 0.85},
        {"name": "Chicago Tribune", "domain": "chicagotribune.com", "reliability_score": 0.85},
        {"name": "Miami Herald", "domain": "miamiherald.com", "reliability_score": 0.8},
        {"name": "Houston Chronicle", "domain": "houstonchronicle.com", "reliability_score": 0.8},
        {"name": "Denver Post", "domain": "denverpost.com", "reliability_score": 0.8},
    ]
    
    for source_data in sources_data:
        existing = db.query(Source).filter(Source.domain == source_data["domain"]).first()
        if not existing:
            source = Source(**source_data)
            db.add(source)
    
    db.commit()
    print("✅ Initial sources created")


def create_initial_locations(db: Session):
    """Create US states and major cities"""
    locations_data = [
        # Major states
        {"state_code": "CA", "state_name": "California"},
        {"state_code": "TX", "state_name": "Texas"},
        {"state_code": "FL", "state_name": "Florida"},
        {"state_code": "NY", "state_name": "New York"},
        {"state_code": "PA", "state_name": "Pennsylvania"},
        {"state_code": "IL", "state_name": "Illinois"},
        {"state_code": "OH", "state_name": "Ohio"},
        {"state_code": "GA", "state_name": "Georgia"},
        {"state_code": "NC", "state_name": "North Carolina"},
        {"state_code": "MI", "state_name": "Michigan"},
        {"state_code": "NJ", "state_name": "New Jersey"},
        {"state_code": "VA", "state_name": "Virginia"},
        {"state_code": "WA", "state_name": "Washington"},
        {"state_code": "AZ", "state_name": "Arizona"},
        {"state_code": "MA", "state_name": "Massachusetts"},
        {"state_code": "TN", "state_name": "Tennessee"},
        {"state_code": "IN", "state_name": "Indiana"},
        {"state_code": "MO", "state_name": "Missouri"},
        {"state_code": "MD", "state_name": "Maryland"},
        {"state_code": "WI", "state_name": "Wisconsin"},
        {"state_code": "CO", "state_name": "Colorado"},
        {"state_code": "MN", "state_name": "Minnesota"},
        {"state_code": "SC", "state_name": "South Carolina"},
        {"state_code": "AL", "state_name": "Alabama"},
        {"state_code": "LA", "state_name": "Louisiana"},
        {"state_code": "KY", "state_name": "Kentucky"},
        {"state_code": "OR", "state_name": "Oregon"},
        {"state_code": "OK", "state_name": "Oklahoma"},
        {"state_code": "CT", "state_name": "Connecticut"},
        {"state_code": "UT", "state_name": "Utah"},
        {"state_code": "IA", "state_name": "Iowa"},
        {"state_code": "NV", "state_name": "Nevada"},
        {"state_code": "AR", "state_name": "Arkansas"},
        {"state_code": "MS", "state_name": "Mississippi"},
        {"state_code": "KS", "state_name": "Kansas"},
        {"state_code": "NM", "state_name": "New Mexico"},
        {"state_code": "NE", "state_name": "Nebraska"},
        {"state_code": "WV", "state_name": "West Virginia"},
        {"state_code": "ID", "state_name": "Idaho"},
        {"state_code": "HI", "state_name": "Hawaii"},
        {"state_code": "NH", "state_name": "New Hampshire"},
        {"state_code": "ME", "state_name": "Maine"},
        {"state_code": "RI", "state_name": "Rhode Island"},
        {"state_code": "MT", "state_name": "Montana"},
        {"state_code": "DE", "state_name": "Delaware"},
        {"state_code": "SD", "state_name": "South Dakota"},
        {"state_code": "ND", "state_name": "North Dakota"},
        {"state_code": "AK", "state_name": "Alaska"},
        {"state_code": "VT", "state_name": "Vermont"},
        {"state_code": "WY", "state_name": "Wyoming"},
    ]
    
    for location_data in locations_data:
        existing = db.query(Location).filter(Location.state_code == location_data["state_code"]).first()
        if not existing:
            location = Location(**location_data)
            db.add(location)
    
    db.commit()
    print("✅ Initial locations created")


def create_incident_categories(db: Session):
    """Create incident categories with keywords"""
    categories_data = [
        {
            "name": "shooting",
            "keywords": '["shooting", "shot", "gun", "firearm", "gunman", "gunshot", "fired shots", "opened fire"]',
            "severity_level": "medium"
        },
        {
            "name": "homicide", 
            "keywords": '["homicide", "murder", "killed", "death", "dead", "fatal", "slain", "victim"]',
            "severity_level": "high"
        },
        {
            "name": "assault",
            "keywords": '["assault", "attacked", "beaten", "injured", "wounded", "violence", "violent"]',
            "severity_level": "low"
        },
        {
            "name": "stabbing",
            "keywords": '["stabbing", "stabbed", "knife", "cut", "slashed", "pierced"]',
            "severity_level": "medium"
        },
        {
            "name": "mass_violence",
            "keywords": '["mass shooting", "mass casualty", "multiple victims", "rampage", "massacre"]',
            "severity_level": "critical"
        },
        {
            "name": "school_incident",
            "keywords": '["school", "campus", "student", "teacher", "education", "university", "college"]',
            "severity_level": "critical"
        },
        {
            "name": "domestic_violence",
            "keywords": '["domestic", "spouse", "partner", "family violence", "abuse"]',
            "severity_level": "medium"
        }
    ]
    
    for category_data in categories_data:
        existing = db.query(IncidentCategory).filter(IncidentCategory.name == category_data["name"]).first()
        if not existing:
            category = IncidentCategory(**category_data)
            db.add(category)
    
    db.commit()
    print("✅ Incident categories created")


def init_database():
    """Initialize database with all seed data"""
    db = SessionLocal()
    try:
        create_initial_sources(db)
        create_initial_locations(db)
        create_incident_categories(db)
        print("🎉 Database initialization complete!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
