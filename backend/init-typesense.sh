#!/bin/bash
set -eo pipefail

# Collection configuration matching typesense_client.py
COLLECTION_NAME="ossfinder"
COLLECTION_SCHEMA=$(cat <<EOF
{
  "name": "$COLLECTION_NAME",
  "fields": [
    {"name": "Id-repo", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "organisation", "type": "string"},
    {"name": "url", "type": "string"},
    {"name": "website", "type": "string"},
    {"name": "description", "type": "string"},
    {"name": "license", "type": "string"},
    {"name": "latest_update", "type": "string"},
    {"name": "language", "type": "string"},
    {"name": "last_commit", "type": "string"},
    {"name": "open_pull_requests", "type": "string"},
    {"name": "master_branch", "type": "string"},
    {"name": "is_fork", "type": "string"},
    {"name": "forked_from", "type": "string"}
  ]
}
EOF
)

# Wait for Typesense to be responsive
wait_for_typesense() {
    local max_attempts=30
    local attempt=0

    echo "Waiting for Typesense to become ready..."
    until curl -sf http://localhost:8108/health; do
        attempt=$((attempt + 1))
        if [ $attempt -ge $max_attempts ]; then
            echo "Typesense failed to start after $max_attempts attempts"
            exit 1
        fi
        sleep 5
    done
}

# Initialize the ossfinder collection
initialize_collection() {
    echo "Initializing Typesense collection..."

    # Check if collection exists
    if curl -sf -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
       http://localhost:8108/collections/${COLLECTION_NAME} >/dev/null; then
        echo "Collection ${COLLECTION_NAME} already exists"
        return
    fi

    # Create collection
    curl -X POST http://localhost:8108/collections \
        -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "${COLLECTION_SCHEMA}"

    echo "Created collection ${COLLECTION_NAME}"
}

# Main execution
wait_for_typesense
initialize_collection