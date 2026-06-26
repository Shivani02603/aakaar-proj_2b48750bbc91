#!/bin/bash
set -euo pipefail

# Run database migrations
alembic upgrade head

# Start the backend server
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000