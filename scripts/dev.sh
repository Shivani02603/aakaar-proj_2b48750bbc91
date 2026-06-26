#!/bin/bash
set -euo pipefail

# Start the backend in the background
docker-compose up -d backend

# Start the frontend development server
cd frontend
npm run dev &

# Wait for all background processes
wait