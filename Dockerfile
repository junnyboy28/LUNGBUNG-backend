FROM python:3.9-slim-bookworm

# Update system packages to latest versions to reduce vulnerabilities
RUN apt-get update && apt-get dist-upgrade -y && apt-get clean

# Ensure latest security patches
RUN apt-get update && apt-get upgrade -y && apt-get clean

WORKDIR /app

# Upgrade system packages and install dependencies for Pillow
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gdown

# Copy application code
COPY . .

# Download models at build time
RUN python download_models.py

# Run the application
# Use shell form to allow environment variable substitution
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT