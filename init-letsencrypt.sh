#!/bin/bash
set -euo pipefail

echo "=== Initializing Let's Encrypt Certificates ==="

# Create required directories
mkdir -p letsencrypt-live nginx/snippets
chmod 755 letsencrypt-live

echo "Requesting certificates from Let's Encrypt..."
docker-compose run --rm certbot sh -c \
  "certbot certonly --webroot -w /var/www/certbot \
  -d finder.green -d www.finder.green \
  --email nina@tymyrddin.dev --agree-tos --non-interactive \
  && cp -Lr /etc/letsencrypt/live /etc/letsencrypt/live-copy \
  && chmod -R 755 /etc/letsencrypt/live-copy"

echo "Starting all services in production mode..."
docker-compose up -d --build

echo "=== Setup completed successfully ==="