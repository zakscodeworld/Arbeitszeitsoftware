# syntax=docker/dockerfile:1

# Stage 1: Install dependencies (no separate builder stage for simplicity here, but can be added for complex builds)
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set working directory
WORKDIR /app

# Install system dependencies if any were needed (e.g., for compiling certain Python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Ensure your requirements.txt includes: fastapi, uvicorn[standard], sqlalchemy, psycopg2-binary, sqlalchemy-utils, passlib[bcrypt]
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# This should be done after creating the user and installing dependencies
# The ownership will be set in docker-compose for dev, or use COPY --chown for prod-like builds
COPY . .

# Ensure the entrypoint script is executable if you have one, e.g., entrypoint.sh
# RUN chmod +x ./entrypoint.sh

USER appuser

# Expose port
EXPOSE 8000

# Default command to run the application
# Ensure main.py and the app object within it are correctly set up
# Updated CMD to wait for DB if using a script, or direct uvicorn if not.
# If you create an entrypoint.sh to wait for the database, use:
# ENTRYPOINT ["/app/entrypoint.sh"] 
# For now, directly running uvicorn:

# Code für ein lokales Deployment
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Code für das neue Deployment
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
