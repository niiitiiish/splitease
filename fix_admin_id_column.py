from sqlalchemy import create_engine, text

# Use the same connection string as in your project
DATABASE_URL = "postgresql://postgres:car24@localhost:5432/splitease"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Drop the foreign key constraint if it exists
    try:
        conn.execute(text("ALTER TABLE groups DROP CONSTRAINT IF EXISTS fk_admin;"))
        print("Foreign key constraint dropped (if it existed).")
    except Exception as e:
        print("Error dropping foreign key:", e)
    # Drop the admin_id column if it exists
    try:
        conn.execute(text("ALTER TABLE groups DROP COLUMN IF EXISTS admin_id;"))
        print("admin_id column dropped (if it existed).")
    except Exception as e:
        print("Error dropping column:", e) 