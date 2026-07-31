FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Calibre and core system libraries for file conversions
RUN apt-get update && apt-get install -y --no-install-recommends \
    calibre \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Install Python dependencies first (leverages Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure upload and output directories exist and grant permissions to appuser
RUN mkdir -p uploads output && chown -R appuser:appuser /app

# Switch from root to non-root user
USER appuser