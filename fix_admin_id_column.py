import sqlalchemy
from sqlalchemy import create_engine, text
import os

# Use the same database URL as your app
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://splitease_user:YjgASMo4UQ7K5M3Ibmmuoazva55qLzpC@dpg-d1qu00jipnbc73epr45g-a.oregon-postgres.render.com/splitease"
)

def add_upi_id_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='upi_id';
        """))
        if not result.fetchone():
            print("Adding upi_id column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN upi_id VARCHAR(100);"))
            print("Column added.")
        else:
            print("upi_id column already exists.")

if __name__ == "__main__":
    add_upi_id_column() 