#!/usr/bin/env python3
"""
Database setup script for Directory
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.database import create_tables, drop_tables
from database.init_data import init_database
from alembic.config import Config
from alembic import command
import argparse


def setup_database():
    """Set up the database with tables and initial data"""
    print("🔧 Setting up Directory database...")
    
    # Create tables
    print("📊 Creating database tables...")
    create_tables()
    print("✅ Tables created successfully")
    
    # Initialize with seed data
    print("🌱 Initializing with seed data...")
    init_database()
    
    print("🎉 Database setup complete!")


def reset_database():
    """Reset the database (drop and recreate)"""
    print("⚠️  Resetting database...")
    
    # Drop all tables
    print("🗑️  Dropping all tables...")
    drop_tables()
    
    # Create tables again
    print("📊 Creating fresh tables...")
    create_tables()
    
    # Initialize with seed data
    print("🌱 Initializing with seed data...")
    init_database()
    
    print("🎉 Database reset complete!")


def run_migrations():
    """Run Alembic migrations"""
    print("🔄 Running database migrations...")
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    print("✅ Migrations completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database setup for Directory")
    parser.add_argument("action", choices=["setup", "reset", "migrate"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "setup":
        setup_database()
    elif args.action == "reset":
        confirm = input("⚠️  This will delete all data. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            reset_database()
        else:
            print("❌ Operation cancelled")
    elif args.action == "migrate":
        run_migrations()
