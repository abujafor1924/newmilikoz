# Gunicorn: Django প্রজেক্টের জন্য বিস্তারিত গাইড

## Gunicorn কি?
Gunicorn (Green Unicorn) হল একটি Python WSGI HTTP সার্ভার, যা প্রোডাকশন সার্ভারে Django অ্যাপ্লিকেশন হোস্ট করার জন্য ব্যবহৃত হয়। এটি Python কোড রান করে ওয়েব সার্ভার (Nginx/Apache) এর সাথে যোগাযোগ করে।

## কেন Gunicorn ব্যবহার করবেন?

### সুবিধা:
- সহজে সেটআপ এবং কনফিগারেশন
- হাই পারফরম্যান্স
- প্রোডাকশন রেডি
- worker প্রসেস ম্যানেজমেন্ট
- Python 3 সম্পূর্ণ সাপোর্ট

## ইনস্টলেশন

```bash
pip install gunicorn
# অথবা requirements.txt এ যোগ করুন
# gunicorn==20.1.0
```

## বেসিক ব্যবহার

### 1. সরাসরি রান
```bash
# প্রজেক্ট ডিরেক্টরিতে
gunicorn your_project.wsgi:application
```

### 2. স্পেসিফিক পোর্টে রান
```bash
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000
```

### 3. ডেমন মোডে রান (ব্যাকগ্রাউন্ডে)
```bash
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000 --daemon
```

## Gunicorn কনফিগারেশন ফাইল তৈরি

`gunicorn_config.py` নামে একটি ফাইল তৈরি করুন:

```python
# gunicorn_config.py

# বাইন্ড এড্রেস এবং পোর্ট
bind = "127.0.0.1:8000"
# bind = "unix:/tmp/gunicorn.sock"  # UNIX socket ব্যবহার করলে

# Worker সেটিংস
workers = 3  # সাধারণত (2 x CPU cores) + 1
worker_class = 'sync'  # বা 'gevent', 'eventlet', 'gthread'
worker_connections = 1000
threads = 2  # worker_class='gthread' এর সাথে ব্যবহার করুন

# পারফরম্যান্স সেটিংস
timeout = 120
keepalive = 5

# লগিং
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# প্রসেস নাম
proc_name = "my_django_project"

# সিকিউরিটি
limit_request_line = 4094
limit_request_fields = 100

# এনভায়রনমেন্ট ভেরিয়েবল
raw_env = [
    'DJANGO_SETTINGS_MODULE=your_project.settings',
    'PYTHONPATH=/path/to/your/project',
]
```

## Systemd সার্ভিস তৈরি (Ubuntu/Debian)

### 1. সার্ভিস ফাইল তৈরি
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

### 2. কন্টেন্ট যোগ করুন:
```ini
[Unit]
Description=gunicorn daemon for Django project
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          your_project.wsgi:application

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. সার্ভিস সক্রিয় করুন
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## Nginx এর সাথে ইন্টিগ্রেশন

### Nginx কনফিগারেশন:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/static/;
        expires 1y;
    }

    location /media/ {
        alias /path/to/your/project/media/;
        expires 1y;
    }
}
```

## Docker এর সাথে Gunicorn

### Dockerfile উদাহরণ:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# ডিপেন্ডেন্সি ইনস্টল
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# প্রজেক্ট কপি
COPY . .

# Gunicorn রান
CMD ["gunicorn", "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "your_project.wsgi:application"]
```

## উন্নত কনফিগারেশন

### 1. Worker প্রসেস ম্যানেজমেন্ট
```python
# Preload app for faster worker spawn
preload_app = True

# Worker timeout
timeout = 30

# Graceful shutdown timeout
graceful_timeout = 30
```

### 2. মেমরি ম্যানেজমেন্ট
```python
# Max requests per worker
max_requests = 1000
max_requests_jitter = 50

# Worker class for async
worker_class = 'gevent'
```

### 3. SSL/TLS কনফিগারেশন
```python
# SSL সক্ষম করুন
keyfile = "/path/to/ssl/key.pem"
certfile = "/path/to/ssl/cert.pem"
ssl_version = "TLS"
```

## মনিটরিং এবং লগিং

### 1. লগ ফরম্যাট কাস্টোমাইজ
```python
# JSON লগ ফরম্যাট
access_log_format = '{"remote_ip":"%(h)s","request_date":"%(t)s","method":"%(m)s","uri":"%(U)s","status":"%(s)s","response_length":"%(B)s","referrer":"%(f)s","user_agent":"%(a)s","response_time":"%(L)s"}'
```

### 2. Prometheus মেট্রিক্স
```bash
pip install prometheus-client
```
```python
from prometheus_client import start_http_server
start_http_server(8001)
```

## ট্রাবলশুটিং

### সাধারণ সমস্যা এবং সমাধান:

**1. Connection refused error**
```bash
# Socket পারমিশন চেক করুন
sudo chmod 755 /run/gunicorn.sock
```

**2. Worker ক্র্যাশ করছে**
```bash
# Error log চেক করুন
tail -f /var/log/gunicorn/error.log

# Worker সংখ্যা কমান
gunicorn --workers 1 your_project.wsgi:application
```

**3. Memory leak**
```python
# config.py এ
max_requests = 1000
max_requests_jitter = 100
```

**4. Slow response**
```bash
# Timeout বাড়ান
gunicorn --timeout 120 your_project.wsgi:application

# Worker class পরিবর্তন
gunicorn --worker-class gevent your_project.wsgi:application
```

## বেস্ট প্রাকটিসেস

1. **Production এ never use `--daemon`** - systemd/supervisor ব্যবহার করুন
2. **Always use reverse proxy** - Nginx/Apache এর পিছনে রাখুন
3. **Monitor resources** - CPU, memory ব্যবহার মনিটর করুন
4. **Use process manager** - systemd, supervisor, circus ব্যবহার করুন
5. **Enable logging** - access এবং error logs সক্রিয় রাখুন
6. **Set appropriate workers** - `(2 x CPU cores) + 1` ফর্মুলা ব্যবহার করুন
7. **Use Unix sockets** - Nginx এর সাথে কমিউনিকেশনের জন্য

## সিকিউরিটি কনফিগারেশন

```python
# Attack protection
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Headers
forwarded_allow_ips = '*'
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
```

## পারফরম্যান্স অপ্টিমাইজেশন

### Worker টিউনিং:
```bash
# ভারী I/O অ্যাপের জন্য
gunicorn --worker-class gevent --workers 5 --threads 2

# CPU ইনটেনসিভ অ্যাপের জন্য
gunicorn --workers 4 --threads 4
```

### Caching সহ:
```python
# Gunicorn কনফিগারেশনে
worker_class = 'gevent'
preload_app = True
max_requests = 1000
```

## অটোমেশন স্ক্রিপ্ট

### Deployment স্ক্রিপ্ট:
```bash
#!/bin/bash
# deploy.sh

echo "Pulling latest changes..."
git pull origin main

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Migrating database..."
python manage.py migrate

echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "Deployment complete!"
```

এই গাইড আপনাকে Gunicorn এর বেসিক থেকে অ্যাডভান্সড ব্যবহার শিখতে সাহায্য করবে। Remember, প্রোডাকশন এ Always test properly before deploying!