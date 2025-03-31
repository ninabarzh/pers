#!/bin/bash
set -euo pipefail

DOMAIN="finder.green"
EMAIL="nina@tymyrddin.dev"
STAGING=${STAGING:-0} # Set to 1 for testing
CERTBOT_FLAGS="--non-interactive --agree-tos --email $EMAIL"

echo "=== Initializing Let's Encrypt Certificates ==="

# Create required directories with proper permissions
echo "Creating certificate directories..."
mkdir -p data/certbot/{conf,www}
chmod -R 755 data/certbot

# Stop and remove existing certbot containers
echo "Cleaning up existing certbot instances..."
docker compose -f docker-compose.prod.yml rm -sf certbot || true

# Start nginx in temporary mode
echo "Starting temporary nginx for certificate issuance..."
docker compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to be ready
echo "Waiting for nginx to start..."
sleep 5

# Request certificates
echo "Requesting certificates for $DOMAIN and www.$DOMAIN..."
if [ "$STAGING" = "1" ]; then
  echo "Using Let's Encrypt staging server (test certificates)"
  CERTBOT_FLAGS="$CERTBOT_FLAGS --staging"
fi

docker compose -f docker-compose.prod.yml run --rm --entrypoint "" certbot \
  sh -c "certbot certonly --webroot -w /var/www/certbot \
  $CERTBOT_FLAGS \
  -d $DOMAIN -d www.$DOMAIN \
  --force-renewal"

# Reconfigure nginx with SSL
echo "Restarting services with SSL configuration..."
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

echo "=== Certificate setup completed successfully ==="
echo "You can now access your site at:"
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"