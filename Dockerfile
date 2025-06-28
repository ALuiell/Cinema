FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Make wait-for-it script executable
RUN chmod +x /app/wait-for-it.py

# Create staticfiles dir
RUN mkdir -p /app/staticfiles

# Default CMD (override in Compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
