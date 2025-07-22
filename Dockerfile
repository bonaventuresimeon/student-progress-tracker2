# Use the official Python 3.11.10 slim image based on Debian Bookworm
FROM python:3.11.10-slim-bookworm

# Set environment variables to prevent Python from writing .pyc files and to ensure output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements.txt first to leverage Docker's cache
COPY requirements.txt .

# Install system dependencies and Python packages from requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential libpq-dev

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8011

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]
