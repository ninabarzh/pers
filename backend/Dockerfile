# backend/Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONPATH=/app/src

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for pytest
ENV PYTHONPATH=/app/src

# Copy the application code and pytest configuration
COPY src/ /app/src/
COPY pyproject.toml /app/

# Set the environment variable for pytest
ENV PYTHONPATH=/app/src

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]