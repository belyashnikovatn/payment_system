#!/bin/bash
# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start the FastAPI app
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
