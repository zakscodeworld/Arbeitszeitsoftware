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
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Wir suchen die URL in verschiedenen Umgebungsvariablen
# Render nutzt manchmal INTERNAL_DATABASE_URL für private Verbindungen
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("INTERNAL_DATABASE_URL") or os.getenv("EXTERNAL_DATABASE_URL")

if DATABASE_URL:
    # Fix für SQLAlchemy (postgres:// wird abgewiesen, muss postgresql:// sein)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"✅ DATABASE_URL aus Umgebungsvariablen gefunden.")
else:
    # 2. Fallback: Lokale Entwicklung (Docker Compose Standardwerte)
    print(f"⚠️ Keine DATABASE_URL gefunden. Nutze Fallback-Werte (lokal).")
    DB_USER = os.getenv("POSTGRES_USER", "pm_user")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    DB_SERVICE_NAME = os.getenv("DATABASE_SERVICE_NAME", "db")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "zeiterfassung_db")
    
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_SERVICE_NAME}:{DB_PORT}/{DB_NAME}"

# Sicherheits-Log (Passwort verstecken)
try:
    safe_host = DATABASE_URL.split("@")[1].split("/")[0]
    print(f"🔌 Versuche Verbindung zu Host: {safe_host}")
except:
    print("🔌 Versuche Verbindung (URL konnte nicht geparst werden)")

# Engine erstellen
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"❌ KRITISCHER FEHLER beim Erstellen der DB-Engine: {e}")
    raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
