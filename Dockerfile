# Use slim Python image
FROM python:3.12-slim


# Set working directory
WORKDIR /app


# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# 2. Copy and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


# 3. Copy project files
COPY . /app


# 4. Start Django application
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
