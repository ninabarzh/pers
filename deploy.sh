#!/bin/bash
set -euo pipefail

# Load sensitive variables from environment (GitHub Secrets)
REQUIRED_VARS=(
  "PROD_DOMAIN"
  "TYPESENSE_API_KEY"
  "PROTON_SMTP_CREDENTIALS"
  "FRIENDLY_CAPTCHA_SECRET"
  "CSRF_SECRET_KEY"
)

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "❌ Missing required variable: $var"
    exit 1
  fi
done

# Cleanup with force removal
echo "=== Cleaning previous deployment ==="
docker-compose -f docker-compose.prod.yml down --volumes --remove-orphans --timeout 30 || true
docker volume prune -f || true
rm -rf /home/deploy/app_data/{typesense,static}/* 2>/dev/null || true

# Secure directory setup
echo "=== Configuring filesystem ==="
sudo mkdir -p \
  /home/deploy/app_data/{typesense,static,certbot/{conf,www}} \
  /home/deploy/app/nginx/config/dhparam

sudo chown -R deploy:docker /home/deploy/app_data
sudo chmod -R 770 /home/deploy/app_data  # More restrictive than 775

# DH params generation (cacheable)
if [ ! -f "/home/deploy/app/nginx/config/dhparam/dhparam.pem" ]; then
  echo "Generating DH parameters (2048-bit)..."
  sudo openssl dhparam -out /home/deploy/app/nginx/config/dhparam/dhparam.pem 2048
  sudo chown deploy:docker /home/deploy/app/nginx/config/dhparam/dhparam.pem
  sudo chmod 600 /home/deploy/app/nginx/config/dhparam/dhparam.pem
fi

# Deploy with build cache busting
echo "=== Deploying services ==="
docker-compose -f docker-compose.prod.yml build --no-cache --pull
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Health verification with timeout
echo "=== Verifying services ==="
TIMEOUT=120
INTERVAL=10
ATTEMPTS=$((TIMEOUT/INTERVAL))

for i in $(seq 1 $ATTEMPTS); do
  if docker-compose -f docker-compose.prod.yml ps | grep -q "(healthy)"; then
    break
  fi
  if [ $i -eq $ATTEMPTS ]; then
    echo "❌ Services did not become healthy within $TIMEOUT seconds"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
  fi
  sleep $INTERVAL
done

# Post-deployment checks
echo "=== Running post-deployment checks ==="
curl -sf https://$PROD_DOMAIN/health || {
  echo "❌ Health check failed"
  exit 1
}

echo "✅ Deployment successful"
echo "🌍 Production URL: https://$PROD_DOMAIN"
echo "🔍 Typesense Dashboard: https://$PROD_DOMAIN:8108"