import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get DATABASE_URL from environment
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./safekeep.db")

# Render uses 'postgres://' but SQLAlchemy requires 'postgresql://'
# This fixes data persistence across deployments
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
    print(f"DATABASE: Using PostgreSQL (converted from postgres://)")
elif DB_URL.startswith("postgresql://"):
    print(f"DATABASE: Using PostgreSQL")
else:
    print(f"DATABASE: Using SQLite (data will NOT persist on redeploy!)")

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) # pylint: disable=invalid-name
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

