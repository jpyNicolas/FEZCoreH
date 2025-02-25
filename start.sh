#!/bin/bash

# Wait for PostgreSQL to be ready
while ! nc -z localhost 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run the initialization script
#alembic revision --autogenerate
#alembic upgrade head
python3 -m app.init_data

# Start the main application
uvicorn app.main:app --host 0.0.0.0 --port 8000
