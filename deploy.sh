#!/bin/bash
set -euo pipefail

# Load environment variables
export $(cat .env | xargs)

# Stop any running containers
docker-compose -f docker-compose.prod.yml down || true

# Pull the latest code
git pull origin main

# Build and start containers
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations if needed
# docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

echo "=== Deployment completed successfully ==="