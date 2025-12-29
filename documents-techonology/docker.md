# Docker এবং Django: বিগিনার থেকে অ্যাডভান্সড

## Docker কি? (বাংলায়)
Docker একটি কন্টেইনারাইজেশন প্ল্যাটফর্ম যা অ্যাপ্লিকেশনগুলোকে তাদের ডিপেন্ডেন্সিসহ আলাদা, পোর্টেবল কন্টেইনারে প্যাকেজ করে। এটি ভার্চুয়াল মেশিনের চেয়ে হালকা এবং দ্রুত।

### Docker এর প্রধান উপাদান:
1. **Docker Image** - অ্যাপ্লিকেশনের ব্লুপ্রিন্ট
2. **Docker Container** - ইমেজের রানিং ইন্সট্যান্স
3. **Dockerfile** - ইমেজ বিল্ড করার নির্দেশনা
4. **Docker Compose** - মাল্টি-কন্টেইনার অ্যাপ পরিচালনা

---

## Django প্রোজেক্টে Docker সেটআপ

### ১. প্রাথমিক সেটআপ

#### Docker ইন্সটলেশন (Ubuntu)
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # রিবুট প্রয়োজন
```

### ২. বেসিক Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Run the application
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### ৩. requirements.txt
```txt
Django==4.2.7
gunicorn==21.2.0
psycopg2-binary==2.9.9
django-cors-headers==4.2.0
django-rest-framework==0.1.0
```

### ৪. Docker Compose ফাইল (বেসিক)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://myuser:mypassword@db:5432/mydb
    depends_on:
      - db

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

---

## অ্যাডভান্সড Docker কনফিগারেশন

### ১. মাল্টি-স্টেজ বিল্ড

```dockerfile
# Multi-stage Dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### ২. Production-ready Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/static
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - django_network

  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=0
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis
    networks:
      - django_network

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    networks:
      - django_network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - django_network

  celery:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A myproject worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - django_network

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A myproject beat --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - django_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  django_network:
    driver: bridge
```

### ৩. Nginx কনফিগারেশন

```nginx
# nginx/nginx.conf
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    
    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
    
    location /static/ {
        alias /app/static/;
    }
    
    location /media/ {
        alias /app/media/;
    }
}
```

### ৪. .env ফাইল

```env
# .env.prod
DB_NAME=production_db
DB_USER=django_user
DB_PASSWORD=strong_password_here
SECRET_KEY=your-secret-key-here
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1
DATABASE_URL=postgres://django_user:strong_password_here@db:5432/production_db
CELERY_BROKER_URL=redis://redis:6379/0
```

---

## Django সেটিংস কনফিগারেশন

```python
# settings.py
import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
DEBUG = os.environ.get('DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mydb'),
        'USER': os.environ.get('DB_USER', 'myuser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'mypassword'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/app/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media/'
```

---

## ইউটিলিটি স্ক্রিপ্টস

### ১. Makefile

```makefile
# Makefile
.PHONY: help build up down logs shell migrate

help:
	@echo "Available commands:"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start containers"
	@echo "  make down      - Stop containers"
	@echo "  make logs      - View container logs"
	@echo "  make shell     - Access web container shell"
	@echo "  make migrate   - Run Django migrations"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f web

shell:
	docker-compose exec web bash

migrate:
	docker-compose exec web python manage.py migrate

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

test:
	docker-compose exec web python manage.py test

createsuperuser:
	docker-compose exec web python manage.py createsuperuser
```

### ২. ডিপ্লয়মেন্ট স্ক্রিপ্ট

```bash
#!/bin/bash
# deploy.sh

echo "Starting deployment..."

# Pull latest changes
git pull origin main

# Build and deploy
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Restart services
docker-compose -f docker-compose.prod.yml restart web

echo "Deployment completed!"
```

---

## বেস্ট প্র্যাকটিসেস

### ১. সিকিউরিটি
```dockerfile
# Non-root user ব্যবহার করুন
RUN useradd -m -u 1000 django
USER django
```

### ২. ইমেজ সাইজ অপটিমাইজেশন
- `.dockerignore` ফাইল ব্যবহার করুন
- Multi-stage builds ব্যবহার করুন
- Unnecessary packages ইনস্টল করবেন না

### ৩. .dockerignore ফাইল
```
.git
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.env
venv
*.sqlite3
media
static
Dockerfile
docker-compose.yml
README.md
```

---

## কমান্ড রেফারেন্স

### বেসিক কমান্ডস
```bash
# ইমেজ বিল্ড
docker build -t my-django-app .

# কন্টেইনার রান
docker run -p 8000:8000 my-django-app

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose exec web python manage.py migrate

# কন্টেইনার ম্যানেজমেন্ট
docker ps
docker images
docker stop <container_id>
docker rm <container_id>
docker rmi <image_id>
```

### প্রোডাকশন ডিপ্লয়মেন্ট
```bash
# Production build
docker-compose -f docker-compose.prod.yml build

# Production run
docker-compose -f docker-compose.prod.yml up -d

# লগ দেখা
docker-compose -f docker-compose.prod.yml logs -f
```

---

## ট্রাবলশুটিং

### সাধারণ সমস্যা ও সমাধান:

1. **Database connection error**
```bash
# Django সেটিংস চেক করুন
docker-compose exec web python manage.py check --database default

# PostgreSQL কানেকশন টেস্ট
docker-compose exec db psql -U myuser -d mydb
```

2. **Permission issues**
```bash
# Volume permissions ফিক্স করুন
sudo chown -R $USER:$USER .
```

3. **ইমেজ ক্লিনআপ**
```bash
# Unused images মুছুন
docker image prune -a

# সব কন্টেইনার মুছুন
docker container prune
```

4. **Docker cache ক্লিয়ার**
```bash
docker builder prune
```

---

এই গাইড আপনাকে Docker সাথে Django ডেভেলপমেন্ট এবং ডিপ্লয়মেন্টের সম্পূর্ণ জার্নি দেখাবে। ধীরে ধীরে Practice করুন এবং Real প্রোজেক্টে Apply করুন।