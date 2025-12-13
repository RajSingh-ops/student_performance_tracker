FROM python:3.11-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry/pip packages
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

CMD ["gunicorn", "yearscore.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
