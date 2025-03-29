#!/bin/bash
set -euo pipefail

DOMAIN="finder.green"
EMAIL="nina@tymyrddin.dev"

echo "=== Initializing Let's Encrypt Certificates ==="

# Create required directories
mkdir -p data/certbot/conf data/certbot/www
chmod -R 755 data/certbot

# Start nginx in temporary mode for ACME challenge
echo "Starting temporary nginx for certificate issuance..."
docker-compose -f docker-compose.prod.yml up --force-recreate --no-deps -d nginx

echo "Requesting certificates from Let's Encrypt..."
docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
  --email ${EMAIL} --agree-tos --non-interactive \
  -d ${DOMAIN} -d www.${DOMAIN}" certbot

# Replace nginx configuration with production version
echo "Configuring nginx for production..."
docker-compose -f docker-compose.prod.yml up -d --force-recreate --no-deps nginx

echo "Starting all services in production mode..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "=== Setup completed successfully ==="