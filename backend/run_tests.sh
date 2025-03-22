#!/bin/bash
# backend/run_tests.sh

# Ensure backend and typesense are running and healthy before executing tests.

# Log environment variables
echo "Environment Variables:"
printenv

# Wait for Typesense to be healthy
echo "Waiting for Typesense to be healthy..."
while ! curl -f http://typesense:8108/health; do
  echo "Typesense not yet healthy. Retrying in 5 seconds..."
  sleep 5
done

# Wait for Backend to be healthy
echo "Waiting for backend to be healthy..."
while ! curl -f http://backend:8000/health; do
  echo "Backend not yet healthy. Retrying in 5 seconds..."
  sleep 5
done

# Run tests
echo "Running backend tests..."
pytest -v tests/

# Include logging and debugging information.
# Capture exit code
TEST_EXIT_CODE=$?

# Log test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "All tests passed!"
else
  echo "Some tests failed. Exit code: $TEST_EXIT_CODE"
fi

# Exit with the test exit code
exit $TEST_EXIT_CODE