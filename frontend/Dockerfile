# frontend/Dockerfile
# frontend/Dockerfile
# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY frontend/requirements-dev.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-dev.txt

RUN mkdir -p /var/www/static && \
    chown -R 1000:1000 /var/www

# Copy application files
COPY frontend/pyproject.toml /app/
COPY frontend/src/ /app/src/

# Install the package in production mode
RUN pip install -e .

# Copy test files
COPY frontend/tests/ /app/tests/
COPY frontend/run_tests.sh /app/

# Copy the .env file
COPY .env /app/.env

# Create and switch to non-root user
RUN useradd -m myuser && \
    chown -R myuser:myuser /app && \
    mkdir -p /app/src/app/static && \
    chown -R myuser:myuser /app/src/app/static
USER myuser

# Expose the port
EXPOSE 8001

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]