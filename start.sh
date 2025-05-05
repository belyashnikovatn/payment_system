#!/bin/bash
# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Starting FastAPI with Alembic migration inside main.py..."
python -m app.main
