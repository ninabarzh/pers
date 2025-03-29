#!/bin/bash

# backend/run_tests.sh
# Ensure backend and typesense are running and healthy before executing tests.

set -e  # Exit immediately if any command fails

# Wait for Typesense to be healthy
echo "Waiting for Typesense to be healthy..."
until curl -fs http://typesense:8108/health >/dev/null; do
  echo "Typesense not yet healthy. Retrying in 3 seconds..."
  sleep 3
done

# Wait for Backend to be healthy (if needed)
echo "Waiting for backend to be healthy..."
until curl -fs http://backend:8000/health >/dev/null; do
  echo "Backend not yet healthy. Retrying in 3 seconds..."
  sleep 3
done

# Add network diagnostics
echo "Network diagnostics:"
ping -c 2 typesense || echo "Ping to typesense failed"
ping -c 2 backend || echo "Ping to backend failed"

# Run tests with increased verbosity
echo "Running backend tests with increased verbosity..."
export PYTHONPATH=/app/src
pytest -vv --log-level=DEBUG tests/

# Capture exit code
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "✅ All backend tests passed!"
else
  echo "❌ Some backend tests failed"
fi

exit $TEST_EXIT_CODE