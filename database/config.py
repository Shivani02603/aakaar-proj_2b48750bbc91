import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base

# Base class for models
Base = declarative_base()

# Read DATABASE_URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Dependency for FastAPI to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the database (create tables)
def init_db():
    Base.metadata.create_all(bind=engine)

# Health check function to test database connection
def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except OperationalError:
        return False