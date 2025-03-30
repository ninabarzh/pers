#!/bin/bash
set -euo pipefail

# Load environment variables
export "$(grep -v '^#' .env | xargs)"

# Stop any running containers
docker-compose -f docker-compose.prod.yml down || true

# Pull the latest code
git pull origin main

# Build and start containers
docker-compose -f docker-compose.prod.yml up -d --build

echo "=== Deployment completed successfully ==="