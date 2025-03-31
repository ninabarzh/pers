#!/bin/bash
set -euo pipefail

# Clean up old volumes
docker volume rm static_volume typesense_data 2>/dev/null || true

# Remove old bind mounts
rm -rf /opt/pers /data/static /data/typesense 2>/dev/null || true

# Load environment variables
export "$(grep -v '^#' .env | xargs)"

# Create required directories with proper permissions
sudo mkdir -p /home/deploy/app_data/{typesense,static,certbot}
sudo chown -R deploy:docker /home/deploy/app_data
sudo chmod -R 775 /home/deploy/app_data

# Create nginx config directory
sudo mkdir -p /home/deploy/app/nginx/config/dhparam
sudo chown -R deploy:docker /home/deploy/app/nginx

# Generate DH params if missing
if [ ! -f "/home/deploy/app/nginx/config/dhparam/dhparam.pem" ]; then
    sudo openssl dhparam -out /home/deploy/app/nginx/config/dhparam/dhparam.pem 2048
    sudo chown deploy:docker /home/deploy/app/nginx/config/dhparam/dhparam.pem
fi

# Fix .env permissions
sudo chown deploy:docker /home/deploy/app/.env
sudo chmod 640 /home/deploy/app/.env

# Stop any running containers
docker-compose -f docker-compose.prod.yml down || true

# Pull the latest code
git pull origin main

# Build and start containers
docker-compose -f docker-compose.prod.yml up -d --build

echo "=== Deployment completed successfully ==="