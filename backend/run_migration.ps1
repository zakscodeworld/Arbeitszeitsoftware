# PowerShell script to run the migration in Docker
# File: run_migration.ps1

# Set the working directory to the project root
Set-Location $PSScriptRoot

# Check if Docker is running
try {
    docker info | Out-Null
}
catch {
    Write-Error "Error: Docker is not running or not installed."
    exit 1
}

# Check if the containers are running
$containersRunning = docker-compose ps | Select-String "zeiterfassung_db"
if (-not $containersRunning) {
    Write-Error "Error: Docker containers are not running. Please start them with 'docker-compose up -d'."
    exit 1
}

# First, copy the migration SQL file to the db container
Write-Host "Copying migration SQL file to container..."
$migrationContent = Get-Content -Path ".\migrations\add_time_columns.sql" -Raw
$migrationContent | docker-compose exec -T db bash -c "cat > /tmp/add_time_columns.sql"

# Run the migration SQL script directly using psql in the container
Write-Host "Applying database migration..."
docker-compose exec db psql -U pm_user -d zeiterfassung_db -f /tmp/add_time_columns.sql

# Check the exit status
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration applied successfully!"
}
else {
    Write-Error "Error applying migration."
    exit 1
}

# Restart the web service to apply the changes
Write-Host "Restarting the web service..."
docker-compose restart web

Write-Host "Migration process completed."
