# Celery ডিটেইলস: ডjango ডেভেলপারদের জন্য বিগিনার থেকে অ্যাডভান্সড (বাংলায়)

## ১. Celery কি এবং কেন প্রয়োজন?

**Celery** একটি **ডিস্ট্রিবিউটেড টাস্ক কিউ** সিস্টেম যা পাইথনে লেখা। Django প্রজেক্টে Celery ব্যবহার করা হয়:

- **লং রানিং টাস্ক** ব্যাকগ্রাউন্ডে রান করানোর জন্য
- **সিডিউলড টাস্ক** (ক্রন জব) এর জন্য
- **এসিনক্রোনাস অপারেশন** এর জন্য
- **হেভি প্রসেসিং** ব্যাকগ্রাউন্ডে অপটিমাইজ করার জন্য

## ২. Celery এর মূল কম্পোনেন্টস

### ২.১. ব্রোকার (Broker)
- **র্যাবিটএমকিউ (RabbitMQ)** - সবচেয়ে জনপ্রিয় (রিকমেন্ডেড)
- **রেডিস (Redis)** - সহজ সেটআপ
- **অ্যামাজন এসকিউএস** - ক্লাউড ভিত্তিক

### ২.২. ওয়ার্কার (Worker)
- টাস্ক এক্সিকিউট করে
- একই সাথে একাধিক ওয়ার্কার রান করা যায়

### ২.৩. ব্যাকএন্ড (Backend)
- টাস্ক রেজাল্ট স্টোর করে
- Redis/Database ব্যবহার করা যায়

## ৩. Celery ইনস্টলেশন ও সেটআপ

### ৩.১. প্যাকেজ ইনস্টলেশন
```bash
pip install celery
pip install redis  # ব্রোকার হিসেবে Redis ব্যবহার করলে
# অথবা
pip install celery[redis]
```

### ৩.২. Django প্রজেক্টে Celery কনফিগারেশন

**প্রোজেক্টের মূল ডিরেক্টরিতে `celery.py` ফাইল তৈরি করুন:**

```python
# your_project/celery.py
import os
from celery import Celery

# Django settings মডিউল সেট করুন
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')

# Django settings থেকে Celery কনফিগারেশন লোড করুন
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django app থেকে টাস্ক অটো-ডিসকভার করুন
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

### ৩.৩. `__init__.py` ফাইল আপডেট করুন
```python
# your_project/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### ৩.৪. `settings.py` এ কনফিগারেশন
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Dhaka'
```

## ৪. প্রথম Celery টাস্ক তৈরি

### ৪.১. সাধারণ টাস্ক
```python
# tasks.py (যেকোনো app এর মধ্যে)
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email(user_email, username):
    """ব্যাকগ্রাউন্ডে ওয়েলকাম মেইল পাঠানো"""
    subject = 'Welcome to Our Platform'
    message = f'Hello {username}, welcome to our platform!'
    from_email = settings.DEFAULT_FROM_EMAIL
    
    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=False,
    )
    return f'Email sent to {user_email}'
```

### ৪.২. ভিউ থেকে টাস্ক কল করা
```python
# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .tasks import send_welcome_email

def register_user(request):
    if request.method == 'POST':
        # ইউজার ক্রিয়েট করার কোড...
        
        # ব্যাকগ্রাউন্ডে মেইল পাঠানো
        send_welcome_email.delay(
            user_email=user.email,
            username=user.username
        )
        
        return JsonResponse({'message': 'Registration successful!'})
```

## ৫. Celery কমান্ডস

### ৫.১. Celery ওয়ার্কার শুরু
```bash
# ডেভেলপমেন্টে
celery -A your_project worker --loglevel=info

# Production এর জন্য
celery -A your_project worker --loglevel=info --concurrency=4
```

### ৫.২. Beat সcheduler (Periodic Tasks)
```bash
celery -A your_project beat --loglevel=info
```

### ৫.৩. ফুল কমান্ড (Worker + Beat)
```bash
celery -A your_project worker --beat --scheduler django --loglevel=info
```

## ৬. পিরিওডিক/সিডিউলড টাস্কস

### ৬.১. `settings.py` এ কনফিগারেশন
```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-daily-report': {
        'task': 'app.tasks.send_daily_report',
        'schedule': crontab(hour=9, minute=0),  # প্রতিদিন সকাল ৯টা
    },
    'cleanup-old-data': {
        'task': 'app.tasks.cleanup_old_data',
        'schedule': crontab(hour=0, minute=0, day_of_week='sunday'),  # প্রতি রবিবার
    },
    'update-exchange-rates': {
        'task': 'app.tasks.update_exchange_rates',
        'schedule': 300.0,  # প্রতি ৫ মিনিটে
    },
}
```

### ৬.২. সিডিউলড টাস্ক উদাহরণ
```python
# tasks.py
@shared_task
def send_daily_report():
    """প্রতিদিনের রিপোর্ট জেনারেট ও পাঠানো"""
    from django.contrib.auth.models import User
    from datetime import date
    
    today = date.today()
    new_users = User.objects.filter(date_joined__date=today).count()
    
    # রিপোর্ট তৈরি ও পাঠানোর লজিক
    # ...
    
    return f"Daily report sent for {today}"
```

## ৭. টাস্ক ম্যানেজমেন্ট ও মনিটরিং

### ৭.১. টাস্ক স্টেটাস চেক
```python
# টাস্ক কল করার সময়
task = send_welcome_email.delay('test@example.com', 'John')
task_id = task.id  # টাস্ক আইডি সংরক্ষণ করুন

# পরে স্টেটাস চেক
from celery.result import AsyncResult
from your_project import celery_app

result = AsyncResult(task_id, app=celery_app)
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # টাস্কের রিটার্ন ভ্যালু
```

### ৭.২. টাস্ক রিট্রাই
```python
@shared_task(bind=True, max_retries=3)
def process_payment(self, user_id, amount):
    try:
        # পেমেন্ট প্রসেসিং লজিক
        # ...
        return "Payment successful"
    except Exception as exc:
        # ৫ মিনিট পর আবার ট্রাই করবে
        raise self.retry(exc=exc, countdown=300)
```

## ৮. এডভান্সড ফিচারস

### ৮.১. চেইন টাস্কস (সিকুয়েন্সিয়াল)
```python
from celery import chain

task_chain = chain(
    task1.s(10, 20),
    task2.s(),
    task3.s()
)
result = task_chain.delay()
```

### ৮.২. গ্রুপ টাস্কস (প্যারালাল)
```python
from celery import group

task_group = group(
    process_image.s(image1),
    process_image.s(image2),
    process_image.s(image3)
)
results = task_group.delay()
```

### ৮.৩. ক্যানভাস (কম্প্লেক্স ওয়ার্কফ্লো)
```python
from celery import chord

header = [download_file.s(url) for url in url_list]
callback = process_results.s()
result = chord(header)(callback)
```

## ৯. Production ডেপ্লয়মেন্ট

### ৯.১. Supervisor কনফিগারেশন
```ini
; /etc/supervisor/conf.d/celery.conf
[program:celery_worker]
command=/path/to/venv/bin/celery -A your_project worker --loglevel=info
directory=/path/to/your_project
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.err.log
autostart=true
autorestart=true
startsecs=10

[program:celery_beat]
command=/path/to/venv/bin/celery -A your_project beat --loglevel=info
directory=/path/to/your_project
user=www-data
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.err.log
autostart=true
autorestart=true
```

### ৯.২. সিস্টেমড সার্ভিস (Systemd)
```ini
; /etc/systemd/system/celery.service
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=ubuntu
Group=ubuntu
EnvironmentFile=/path/to/celery.env
WorkingDirectory=/path/to/your_project
ExecStart=/path/to/venv/bin/celery multi start worker -A your_project
ExecStop=/path/to/venv/bin/celery multi stop worker -A your_project
ExecReload=/path/to/venv/bin/celery multi restart worker -A your_project

[Install]
WantedBy=multi-user.target
```

## ১০. বেস্ট প্রাকটিসেস

### ১০.১. টাস্ক আইডেমপোটেন্ট বানান
```python
@shared_task(bind=True)
def update_user_stats(self, user_id):
    """আইডেমপোটেন্ট টাস্ক - বারবার রান করালেও সমস্যা নেই"""
    user = User.objects.get(id=user_id)
    
    # লক মেকানিজম ব্যবহার
    lock_id = f'update_user_stats_{user_id}'
    
    # Distributed lock (Redis ব্যবহার করে)
    with cache.lock(lock_id, timeout=60):
        # স্ট্যাটস আপডেট লজিক
        pass
```

### ১০.২. টাস্ক টাইমআউট সেট করুন
```python
@shared_task(bind=True, soft_time_limit=60, time_limit=120)
def long_running_task(self):
    """৬০ সেকেন্ডের মধ্যে শেষ হওয়া উচিত"""
    # লং রানিং প্রসেস
    pass
```

### ১০.৩. এডভান্সড কনফিগারেশন
```python
# settings.py
CELERY_TASK_ROUTES = {
    'app.tasks.heavy_task': {'queue': 'heavy'},
    'app.tasks.light_task': {'queue': 'light'},
}

CELERY_TASK_ANNOTATIONS = {
    'app.tasks.send_email': {'rate_limit': '10/m'},  # প্রতি মিনিটে ১০টি
}

CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
CELERY_TASK_TRACK_STARTED = True
```

## ১১. ট্রাবলশুটিং ও ডিবাগিং

### সাধারণ সমস্যা ও সমাধান:
1. **টাস্ক কাজ করছে না** → Celery worker চেক করুন
2. **রেজাল্ট না আসা** → Result backend কনফিগারেশন চেক করুন
3. **মেমরি লিক** → `max-tasks-per-child` সেট করুন
4. **ব্রোকার কানেকশন** → Redis/RabbitMQ সার্ভিস চেক করুন

### ডিবাগিং টিপস:
```python
# টাস্কে লগিং যোগ করুন
import logging
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def debug_task(self):
    logger.info(f"Task started: {self.request.id}")
    # টাস্ক লজিক
    logger.info("Task completed successfully")
```

## ১২. Celery ফ্লাওয়ার মনিটরিং

ফ্লাওয়ার একটি ওয়েব-ভিত্তিক Celery মনিটরিং টুল:

```bash
pip install flower
celery -A your_project flower --port=5555
```

এরপর ব্রাউজারে `http://localhost:5555` ভিজিট করুন।

---

## শেষ কথাঃ

Celery শেখার জন্য ধাপে ধাপে এগোউন:

1. **বিগিনার**: সাধারণ টাস্ক তৈরি ও রান করা
2. **ইন্টারমিডিয়েট**: Periodic tasks, Task results, Error handling
3. **অ্যাডভান্সড**: Task routing, Monitoring, Production deployment
4. **এক্সপার্ট**: Distributed tasks, Performance optimization, Custom brokers

প্রথমে **Redis** ব্রোকার ব্যবহার করে শুরু করুন, কারণ এটি সেটআপে সহজ। ছোট ছোট টাস্ক দিয়ে শুরু করুন, যেমন: ইমেইল সেন্ডিং, ফাইল প্রসেসিং, API কল ইত্যাদি।

Celery দক্ষতা ডjango ডেভেলপার হিসেবে আপনার ভ্যালু অনেক বাড়িয়ে দেবে, বিশেষ করে যখন স্কেলেবল অ্যাপ্লিকেশন বানাবেন।