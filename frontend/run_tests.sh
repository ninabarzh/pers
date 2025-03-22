#!/bin/bash
# frontend/run_tests.sh

# Ensure frontend is running and healthy before executing tests.

# Log environment variables
echo "Environment Variables:"
printenv

# Ensure the frontend service is healthy
echo "Waiting for frontend to be healthy..."
while ! curl -f http://frontend:8001/health; do
  echo "Frontend not yet healthy. Retrying in 5 seconds..."
  sleep 5
done

# Run tests with verbose output
echo "Running frontend tests..."
pytest -v tests/

# Include logging and debugging information.
# Capture exit code
TEST_EXIT_CODE=$?

# Log test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "All frontend tests passed!"
else
  echo "Some frontend tests failed. Exit code: $TEST_EXIT_CODE"
fi

# Exit with the test exit code
exit $TEST_EXIT_CODE