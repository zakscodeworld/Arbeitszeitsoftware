#!/bin/bash
# run_migration.sh - A script to run the migration inside the Docker container

# Set the working directory to the project root
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "Error: Docker is not running or not installed."
  exit 1
fi

# Check if the containers are running
if ! docker-compose ps | grep -q "zeiterfassung_db"; then
  echo "Error: Docker containers are not running. Please start them with 'docker-compose up -d'."
  exit 1
fi

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
timeout=30
elapsed=0
while [ $elapsed -lt $timeout ]; do
  if docker-compose exec db pg_isready -U pm_user -d zeiterfassung_db -q; then
    break
  fi
  sleep 1
  elapsed=$((elapsed + 1))
done

if [ $elapsed -ge $timeout ]; then
  echo "Error: Database did not become ready within $timeout seconds."
  exit 1
fi

echo "Database is ready."

# Run the migration SQL script directly using psql in the container
echo "Applying database migration..."
docker-compose exec db psql -U pm_user -d zeiterfassung_db -f /tmp/add_time_columns.sql

# Check the exit status
if [ $? -eq 0 ]; then
  echo "Migration applied successfully!"
else
  echo "Error applying migration."
  exit 1
fi

# Restart the web service to apply the changes
echo "Restarting the web service..."
docker-compose restart web

echo "Migration process completed."
