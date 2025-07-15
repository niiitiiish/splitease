from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use the DATABASE_URL from environment if set, otherwise use the provided Render URL
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://splitease_user:YjgASMo4UQ7K5M3Ibmmuoazva55qLzpC@dpg-d1qu00jipnbc73epr45g-a.oregon-postgres.render.com/splitease"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
