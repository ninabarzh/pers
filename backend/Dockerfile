# backend/Dockerfile
# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl iputils-ping && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ /app/src/
COPY pyproject.toml /app/
COPY run_tests.sh /app/

# Create a non-root user and switch to it
RUN useradd -m myuser && \
    chown -R myuser:myuser /app  # Change ownership of /app
USER myuser

# Expose the port the app runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]