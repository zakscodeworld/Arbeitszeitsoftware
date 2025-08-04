import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables for database connection
# These should be set in your .env file and loaded by docker-compose
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_SERVICE_NAME = os.getenv("DATABASE_SERVICE_NAME", "db") # Default to 'db' if not set
DB_PORT = os.getenv("DATABASE_PORT", "5432")             # Default to '5432' if not set
DB_NAME = os.getenv("POSTGRES_DB")

# Construct the SQLAlchemy database URL for PostgreSQL
# Ensure all components are present, otherwise, this will fail
if not all([DB_USER, DB_PASSWORD, DB_SERVICE_NAME, DB_PORT, DB_NAME]):
    raise ValueError("One or more database connection environment variables are not set.")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_SERVICE_NAME}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables. Call this from main.py on startup.
def init_db():
    # Import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db().
    # from . import models # Assuming models.py is in the same directory
    # Base.metadata.create_all(bind=engine)
    # print("Database tables created (if they didn't exist).")
    # The actual table creation will be called from main.py
    pass