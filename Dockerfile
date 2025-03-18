FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run linting
RUN flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
RUN black --check src tests
RUN isort --check-only --profile black src tests

# Run tests
RUN pytest --cov=src tests/

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Command to run the application
WORKDIR /app/src
CMD ["python", "-m", "api.run"] 