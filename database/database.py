"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://adminwatch:adminwatch123@localhost/directory")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all tables in the database
    """
    from .models import Base
    Base.metadata.drop_all(bind=engine)
