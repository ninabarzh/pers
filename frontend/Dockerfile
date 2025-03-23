# frontend/Dockerfile
# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY frontend/src/ /app/src/
COPY frontend/pyproject.toml /app/

# Copy test files
COPY frontend/tests/ /app/tests/
COPY frontend/run_tests.sh /app/

# Copy the .env.dev file from the root directory
COPY .env.dev .env.dev
COPY .env.prod .env.prod

# Create a non-root user and switch to it
RUN useradd -m myuser && \
    chown -R myuser:myuser /app  # Change ownership of /app
USER myuser

# Expose the port the app runs on
EXPOSE 8001

# Command to run the application (default)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]