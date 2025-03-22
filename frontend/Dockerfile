# frontend/Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for pytest
ENV PYTHONPATH=/app/src

# Copy the application code and pytest configuration
COPY src/ /app/src/
COPY pyproject.toml /app/

# Copy test.json to /app/tests/
COPY tests/test.json /app/tests/test.json

# Command to run the application (default)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]