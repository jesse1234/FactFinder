# Use the official lightweight Python image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Copy only requirements file to leverage Docker cache
COPY requirements.txt /app/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port Flask will run on
EXPOSE 8080

# Add Google Cloud Run environment variables
ENV PORT=8080

# Command to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
