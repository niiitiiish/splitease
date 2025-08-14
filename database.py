from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get DATABASE_URL from environment (set in Render dashboard)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # If using Neon, ensure SSL mode is set
    if "neon.tech" in DATABASE_URL and "sslmode" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"
else:
    # Use Neon database as default (since Render database is expired)
    DATABASE_URL = "postgresql://neondb_owner:npg_1AxtOX3Jlvud@ep-weathered-boat-ad256w08-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
