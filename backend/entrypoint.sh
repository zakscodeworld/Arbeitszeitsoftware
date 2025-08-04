#!/bin/bash
set -e

# Function to check if PostgreSQL is ready
wait_for_pg() {
    echo "Waiting for PostgreSQL at $DATABASE_SERVICE_NAME:$DATABASE_PORT..."
    python healthcheck.py "$DATABASE_SERVICE_NAME" "$DATABASE_PORT"
    echo "PostgreSQL is ready!"
}

# Function to apply database migrations
apply_migrations() {
    echo "Applying database migrations..."
    python apply_migration.py
    echo "Migrations completed!"
}

# Function to start the application
start_app() {
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "Starting application in production mode..."
        gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
    else
        echo "Starting application in development mode..."
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    fi
}

# Main execution
echo "Starting service with ENVIRONMENT=$ENVIRONMENT"
wait_for_pg
apply_migrations
start_app
