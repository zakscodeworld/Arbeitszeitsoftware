#!/usr/bin/env python
# apply_migration.py - Script to apply the database migration for time entry columns

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import database config from the main app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SQLALCHEMY_DATABASE_URL

def apply_migration():
    """Apply the SQL migration to add startzeit and endzeit columns"""
    print("Starting migration to add time columns to zeiteintraege table...")
    
    # Create database connection
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Read the migration SQL file
        migration_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "migrations", 
            "add_time_columns.sql"
        )
        
        with open(migration_file_path, 'r') as file:
            migration_sql = file.read()
        
        # Execute the migration
        print("Executing SQL migration...")
        db.execute(text(migration_sql))
        db.commit()
        print("Migration applied successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error applying migration: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    apply_migration()
