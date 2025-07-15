from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use your actual password
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:car24@localhost:5432/splitease"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ This must be here
Base = declarative_base()
