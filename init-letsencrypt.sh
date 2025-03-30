#!/bin/bash
set -euo pipefail

DOMAIN="finder.green"
EMAIL="nina@tymyrddin.dev"
STAGING=${STAGING:-0} # Set to 1 for testing

echo "=== Initializing Let's Encrypt Certificates ==="

# Create required directories
mkdir -p data/certbot/{conf,www}
chmod -R 755 data/certbot

# Stop any running nginx
docker compose -f docker-compose.prod.yml down nginx || true

# Start nginx in temporary mode
echo "Starting temporary nginx for certificate issuance..."
docker compose -f docker-compose.prod.yml up -d nginx

# Request certificates
echo "Requesting certificates from Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
  --email $EMAIL --agree-tos --non-interactive \
  --staging $STAGING \
  -d $DOMAIN -d www.$DOMAIN" certbot

# Reconfigure nginx with SSL
echo "Configuring nginx for production..."
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

echo "=== Certificate setup completed successfully ==="