# Use the official lightweight Python image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port Flask will run on
EXPOSE 8080

# Add Google Cloud Run environment variables
ENV PORT=8080

# Command to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
