"""
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
"""
# Neue Struktur 

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. PRÜFUNG: Gibt es eine fertige Datenbank-URL 
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Fix für Render: Render beginnt URLs oft mit "postgres://", 
    # aber SQLAlchemy benötigt "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # 2. FALLBACK: Wir sind lokal (Docker), baue die URL selbst
    DB_USER = os.getenv("POSTGRES_USER", "pm_user")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    DB_SERVICE_NAME = os.getenv("DATABASE_SERVICE_NAME", "db")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "zeiterfassung_db")
    
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_SERVICE_NAME}:{DB_PORT}/{DB_NAME}"

print(f"Verbinde mit Datenbank unter: {DATABASE_URL.split('@')[-1]}") # Loggt den Host (ohne Passwort)

# Engine erstellen
engine = create_engine(DATABASE_URL)

# Session erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
