# backend/Dockerfile
# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl iputils-ping && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements-dev.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copy application files
COPY backend/pyproject.toml /app/
COPY backend/src/ /app/src/

# Install the package in production mode
RUN pip install -e .

# Copy test files
COPY backend/tests/ /app/tests/
COPY backend/run_tests.sh /app/

# Copy the .env file
COPY .env /app/.env

# Create and switch to non-root user
RUN useradd -m myuser && \
    chown -R myuser:myuser /app
USER myuser

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]