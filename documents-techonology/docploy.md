# Django-তে Deployment: বিগিনার থেকে অ্যাডভান্সড

## ধাপ ১: প্রস্তুতি (বিগিনার লেভেল)

### ১.১ প্রজেক্ট সেটআপ
```bash
# ভার্চুয়াল এনভায়রনমেন্ট তৈরি
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Django ইনস্টল
pip install django
pip install gunicorn psycopg2-binary
```

### ১.২ প্রজেক্ট তৈরি
```bash
django-admin startproject myproject
cd myproject
python manage.py startapp myapp
```

### ১.৩ settings.py কনফিগারেশন
```python
# settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

DEBUG = False  # Production এ False করুন

ALLOWED_HOSTS = ['your-domain.com', 'localhost', '127.0.0.1']

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files জন্য
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

## ধাপ ২: প্রোডাকশন সেটিংস (ইন্টারমিডিয়েট লেভেল)

### ২.১ requirements.txt তৈরি
```bash
pip freeze > requirements.txt
```

### ২.২ runtime.txt তৈরি (Python version নির্ধারণ)
```
python-3.9.13
```

### ২.৩ Procfile তৈরি (Heroku জন্য)
```
web: gunicorn myproject.wsgi --log-file -
release: python manage.py migrate
```

### ২.৪ wsgi.py কনফিগারেশন
```python
# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
application = get_wsgi_application()
```

## ধাপ ৩: বিভিন্ন প্লাটফর্মে Deployment

### ৩.১ Heroku-তে Deployment

#### Heroku CLI ইনস্টল
```bash
# Windows
curl https://cli-assets.heroku.com/install-standalone.exe -o heroku-installer.exe

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Deployment স্টেপস
```bash
# Heroku login
heroku login

# Heroku app তৈরি
heroku create my-django-app

# Environment variables সেট
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=my-django-app.herokuapp.com

# Database যোগ (PostgreSQL)
heroku addons:create heroku-postgresql:hobby-dev

# Code push
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a my-django-app
git push heroku main

# Database migrate
heroku run python manage.py migrate

# Superuser তৈরি
heroku run python manage.py createsuperuser
```

### ৩.২ PythonAnywhere-তে Deployment

#### স্টেপস:
1. PythonAnywhere একাউন্ট তৈরি করুন
2. Web app তৈরি করুন
3. Virtual environment সেটআপ করুন
4. Git থেকে code clone করুন
5. Database কনফিগার করুন (MySQL)
6. Static files collect করুন
7. WSGI configuration সেট করুন

#### WSGI Configuration:
```python
# /var/www/yourusername_pythonanywhere_com_wsgi.py
import os
import sys

path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### ৩.৩ AWS EC2-তে Deployment (অ্যাডভান্সড)

#### Step 1: EC2 Instance তৈরি
1. AWS Console থেকে EC2 সার্ভিস নির্বাচন
2. Ubuntu Server 22.04 LTS নির্বাচন
3. Key pair তৈরি
4. Security group এ ports খুলুন:
   - 80 (HTTP)
   - 443 (HTTPS)
   - 22 (SSH)

#### Step 2: SSH করে কানেক্ট
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

#### Step 3: সার্ভার সেটআপ
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-dev libpq-dev nginx curl -y

# Install virtualenv
sudo pip3 install virtualenv

# Project directory তৈরি
mkdir ~/myproject
cd ~/myproject

# Virtual environment
virtualenv venv
source venv/bin/activate

# Django install
pip install django gunicorn psycopg2-binary
```

#### Step 4: Gunicorn সেটআপ
```bash
# Gunicorn service file তৈরি
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/myproject
ExecStart=/home/ubuntu/myproject/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/ubuntu/myproject/myproject.sock \
          myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Gunicorn start
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

#### Step 5: Nginx কনফিগারেশন
```bash
sudo nano /etc/nginx/sites-available/myproject
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/ubuntu/myproject;
    }
    
    location /media/ {
        root /home/ubuntu/myproject;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/myproject/myproject.sock;
    }
}
```

```bash
# Symbolic link তৈরি
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled

# Nginx restart
sudo systemctl restart nginx
```

#### Step 6: SSL Certificate (Let's Encrypt)
```bash
# Certbot install
sudo apt install certbot python3-certbot-nginx -y

# SSL certificate তৈরি
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## ধাপ ৪: ডাটাবেস কনফিগারেশন (অ্যাডভান্সড)

### PostgreSQL সেটআপ (AWS RDS)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database_name',
        'USER': 'database_user',
        'PASSWORD': 'database_password',
        'HOST': 'your-rds-endpoint',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',
        }
    }
}
```

### Database Backup & Recovery
```bash
# Backup
pg_dump -h localhost -U username dbname > backup.sql

# Restore
psql -h localhost -U username dbname < backup.sql
```

## ধাপ ৫: Performance Optimization (অ্যাডভান্সড)

### ৫.১ Caching সেটআপ
```python
# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session cache
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### ৫.২ CDN কনফিগারেশন (AWS CloudFront)
```python
# settings.py
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Static files
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

# Media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

### ৫.৩ Database Optimization
```python
# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection persistence
        'CONN_HEALTH_CHECKS': True,
    }
}
```

## ধাপ ৬: Monitoring & Logging (অ্যাডভান্সড)

### ৬.১ Logging কনফিগারেশন
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### ৬.২ Performance Monitoring (New Relic/Sentry)
```python
# settings.py

# New Relic
NEW_RELIC_CONFIG_FILE = '/path/to/newrelic.ini'

# Sentry
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

## ধাপ ৭: CI/CD Pipeline (অ্যাডভান্সড)

### GitHub Actions workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Django App

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Heroku
      env:
        HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
      run: |
        git remote add heroku https://heroku:${{ secrets.HEROKU_API_KEY }}@git.heroku.com/${{ secrets.HEROKU_APP_NAME }}.git
        git push heroku main
```

## সাধারণ Errors এবং Solutions:

### ১. Static files না দেখানো
```bash
# Collect static files
python manage.py collectstatic

# Whitenoise install
pip install whitenoise
```

### ২. Database connection error
```python
# settings.py
import dj_database_url
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
```

### ৩. Timezone issue
```python
TIME_ZONE = 'Asia/Dhaka'
USE_TZ = True
```

### ৪. Media files না দেখা
```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Deployment Checklist:

### Before Deployment:
- [ ] DEBUG = False সেট করা
- [ ] ALLOWED_HOSTS সেট করা
- [ ] SECRET_KEY environment variable আনা
- [ ] Database production-ready করা
- [ ] Static files collect করা
- [ ] CSRF_TRUSTED_ORIGINS সেট করা
- [ ] Security settings enable করা

### After Deployment:
- [ ] Website load test করা
- [ ] SSL certificate check করা
- [ ] Database backup সেটআপ
- [ ] Error monitoring সেটআপ
- [ ] Performance monitoring সেটআপ

## Important Tips:
1. সবসময় version control (Git) ব্যবহার করুন
2. Environment variables ব্যবহার করুন sensitive data এর জন্য
3. Regular backup নিন
4. Security updates রাখুন
5. Monitoring tools ব্যবহার করুন
6. Load testing করুন production এ যাওয়ার আগে

এই গাইডটি ধাপে ধাপে Django deployment শিখতে সাহায্য করবে। ছোট প্রজেক্ট দিয়ে শুরু করে gradually advance লেভেলের দিকে যান।