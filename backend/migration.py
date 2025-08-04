#!/usr/bin/env python
# migration.py - A standalone script to apply database migrations

import os
import sys
import subprocess
import time

def run_psql_command(command, retries=5, delay=2):
    """Run a PostgreSQL command using environment variables from .env"""
    # Load environment variables from .env file
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Construct the psql command
    cmd = [
        "psql",
        "-h", env_vars.get("DATABASE_SERVICE_NAME", "db"),
        "-U", env_vars.get("POSTGRES_USER", "pm_user"),
        "-d", env_vars.get("POSTGRES_DB", "zeiterfassung_db"),
        "-c", command
    ]
    
    # Set PGPASSWORD environment variable for authentication
    env = os.environ.copy()
    env["PGPASSWORD"] = env_vars.get("POSTGRES_PASSWORD", "your_strong_password")
    
    # Try to execute the command with retries
    for attempt in range(retries):
        try:
            print(f"Executing SQL command (attempt {attempt+1}/{retries})...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print("Command executed successfully!")
                print(result.stdout)
                return True
            else:
                print(f"Command failed with error: {result.stderr}")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        except Exception as e:
            print(f"Error executing command: {str(e)}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    return False

def run_migration_file(file_path):
    """Execute a SQL migration file"""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        print(f"Executing migration from {file_path}...")
        return run_psql_command(sql_content)
    except Exception as e:
        print(f"Error running migration file: {str(e)}")
        return False

def apply_all_migrations():
    """Apply all migration files in the migrations directory"""
    migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
    if not os.path.exists(migrations_dir):
        print(f"Creating migrations directory at {migrations_dir}")
        os.makedirs(migrations_dir)
    
    # Check if the time columns migration file exists
    time_columns_migration = os.path.join(migrations_dir, "add_time_columns.sql")
    if not os.path.exists(time_columns_migration):
        print(f"Creating default time columns migration file at {time_columns_migration}")
        with open(time_columns_migration, 'w') as f:
            f.write("""-- Add startzeit and endzeit columns to zeiteintraege table
-- First add columns as nullable to allow for existing data
ALTER TABLE zeiteintraege 
ADD COLUMN IF NOT EXISTS startzeit TIME,
ADD COLUMN IF NOT EXISTS endzeit TIME;

-- Update any existing records with default values (8:00 AM to 5:00 PM)
-- This ensures we don't have NULL values in existing records
UPDATE zeiteintraege
SET startzeit = '08:00:00',
    endzeit = '17:00:00'
WHERE startzeit IS NULL OR endzeit IS NULL;

-- Now set the columns to NOT NULL to match the model definition
ALTER TABLE zeiteintraege
ALTER COLUMN startzeit SET NOT NULL,
ALTER COLUMN endzeit SET NOT NULL;
""")
    
    # Apply the migration
    success = run_migration_file(time_columns_migration)
    if success:
        print("Time columns migration applied successfully!")
    else:
        print("Failed to apply time columns migration.")

if __name__ == "__main__":
    print("Starting database migration process...")
    apply_all_migrations()
    print("Migration process completed.")
