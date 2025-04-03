#!/bin/bash
set -euo pipefail

DOMAIN="finder.green"
EMAIL="nina@tymyrddin.dev"
# Also, do create the necessary directories on the server

echo "=== Setting up SSL certificates ==="

# Stop any running services
docker compose -f docker-compose.prod.yml down || true

# Start nginx without SSL to serve ACME challenge
echo "Starting temporary web server..."
docker compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to be ready
sleep 5

# Request certificates
echo "Requesting certificates for $DOMAIN..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint "" certbot \
  sh -c "certbot certonly --webroot -w /var/www/certbot \
  --email $EMAIL --agree-tos --non-interactive \
  -d $DOMAIN -d www.$DOMAIN \
  --force-renewal"

# Restart services with SSL
echo "Restarting with SSL configuration..."
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

echo "=== SSL setup completed successfully ==="
echo "Access your site at:"
echo "https://$DOMAIN"
