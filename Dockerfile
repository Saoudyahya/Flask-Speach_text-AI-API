# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code to the working directory
COPY Speach_text.py /app/
COPY requirements.txt /app/

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploads /app/whisper_models

# Expose the application's port
EXPOSE 5000

# Run the application
CMD ["python", "Speach_text.py"]
