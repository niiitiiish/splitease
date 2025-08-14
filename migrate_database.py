#!/usr/bin/env python3
"""
Database migration script for SpliEase
Run this to set up your new database
"""

import os
from sqlalchemy import create_engine, text
from database import Base, engine
from models import User, Group, Expense, Invitation, Settlement

def test_connection():
    """Test the database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"   PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create all tables in the database"""
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if not existing_user:
            # Create a sample user
            sample_user = User(
                username="admin",
                password="admin123",  # In production, use proper password hashing
                upi_id="admin@upi"
            )
            db.add(sample_user)
            
            # Create a sample group
            sample_group = Group(name="Roommates")
            db.add(sample_group)
            db.commit()
            
            print("✅ Sample data created successfully!")
            print("   - Username: admin")
            print("   - Password: admin123")
            print("   - Group: Roommates")
        else:
            print("✅ Sample data already exists!")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    print("🚀 SpliEase Database Migration")
    print("=" * 30)
    
    # Check if DATABASE_URL is set
    if not os.environ.get("DATABASE_URL"):
        print("⚠️  DATABASE_URL environment variable not set!")
        print("Please set your database connection string as DATABASE_URL")
        print("For Neon: postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require")
        return
    
    # Test connection
    if not test_connection():
        return
    
    # Create tables
    if not create_tables():
        return
    
    # Create sample data
    create_sample_data()
    
    print("\n🎉 Database setup completed successfully!")
    print("Your SpliEase app is ready to use!")

if __name__ == "__main__":
    main() 