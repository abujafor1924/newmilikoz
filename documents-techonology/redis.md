# Redis ও Django ডেভেলপার গাইড: বিগিনার থেকে অ্যাডভান্সড (বাংলা)

## Redis পরিচিতি (In-Memory Data Structure Store)

### Redis কি?
Redis (Remote Dictionary Server) একটি **ইন-মেমরি ডেটা স্ট্রাকচার স্টোর** যা ডেটাবেস, ক্যাশে, মেসেজ ব্রোকার হিসাবে ব্যবহৃত হয়। এটি **key-value** স্টোর হিসেবে কাজ করে।

### Redis-এর বৈশিষ্ট্য:
- **ইন-মেমরি ডেটা স্টোর**: সব ডেটা মেমরিতে থাকে
- **পারসিসটেন্স**: ডিস্কে ডেটা সেভ করার অপশন আছে
- **ডাটা স্ট্রাকচার**: Strings, Lists, Sets, Hashes, Sorted Sets
- **রেপ্লিকেশন**: Master-Slave রেপ্লিকেশন সাপোর্ট করে
- **হাই পারফরম্যান্স**: সেকেন্ডে লক্ষাধিক রিকোয়েস্ট হ্যান্ডল করতে পারে

### Redis ইনস্টলেশন (Ubuntu):
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

## Django Redis ইন্টিগ্রেশন

### Django-তে Redis সেটআপ:

**১. প্যাকেজ ইন্সটল করুন:**
```bash
pip install django-redis redis
```

**২. settings.py কনফিগারেশন:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# সেশন স্টোরেজ Redis-এ রাখা
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Redis ব্যবহারের বিভিন্ন ক্ষেত্র Django-তে

### ১. ক্যাশিং সিস্টেম
```python
from django.core.cache import cache

# ডেটা ক্যাশে করা
def get_user_data(user_id):
    cache_key = f'user_data_{user_id}'
    data = cache.get(cache_key)
    
    if data is None:
        # ডেটাবেস থেকে ডেটা আনুন
        data = User.objects.get(id=user_id)
        # ১ ঘন্টার জন্য ক্যাশে করুন
        cache.set(cache_key, data, 3600)
    
    return data

# ক্যাশে ডিলিট করা
cache.delete('user_data_123')
```

### ২. সেশন ম্যানেজমেন্ট
```python
# views.py
def login_view(request):
    # ইউজার লগিন লজিক
    request.session['user_id'] = user.id
    request.session.set_expiry(86400)  # 24 ঘন্টা

def dashboard_view(request):
    user_id = request.session.get('user_id')
    # ... বাকি কোড
```

### ৩. রেট লিমিটিং (API থ্রটলিং)
```python
from django.core.cache import cache
from django.http import HttpResponse
import time

def rate_limit_view(request):
    ip = request.META.get('REMOTE_ADDR')
    key = f'rate_limit:{ip}'
    
    # বর্তমান রিকোয়েস্ট কাউন্ট
    current = cache.get(key, 0)
    
    if current >= 10:  # ১ মিনিটে ১০ রিকোয়েস্ট
        return HttpResponse('Rate limit exceeded', status=429)
    
    cache.incr(key)
    if current == 0:
        cache.expire(key, 60)  # ১ মিনিট expire
    
    return HttpResponse('Success')
```

### ৪. সেলারি টাস্ক কিউ
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# tasks.py
from celery import shared_task

@shared_task
def send_email_task(user_email, message):
    # ইমেল সেন্ডিং লজিক
    send_mail(
        'Subject',
        message,
        'from@example.com',
        [user_email]
    )
    return 'Email sent'
```

## Redis ডেটা স্ট্রাকচার ব্যবহার

### ১. Strings (সাধারণ key-value)
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# ডেটা সেট করা
r.set('user:1:name', 'John Doe')
r.setex('temp:token', 300, 'abc123')  # ৫ মিনিট expire

# ডেটা পাওয়া
name = r.get('user:1:name')
```

### ২. Hashes (অবজেক্ট স্টোর)
```python
# হ্যাশ তৈরি
r.hset('user:1', 'name', 'John')
r.hset('user:1', 'email', 'john@example.com')
r.hset('user:1', 'age', 30)

# সব ফিল্ড পড়া
user_data = r.hgetall('user:1')
# নির্দিষ্ট ফিল্ড পড়া
name = r.hget('user:1', 'name')
```

### ৩. Lists (কিউ হিসেবে ব্যবহার)
```python
# লিস্টে আইটেম যুক্ত করা
r.lpush('tasks', 'task1')
r.rpush('tasks', 'task2')

# আইটেম বের করা
task = r.lpop('tasks')  # প্রথম আইটেম
```

### ৪. Sets (ইউনিক আইটেম)
```python
# সেটে আইটেম যুক্ত
r.sadd('online_users', 'user1')
r.sadd('online_users', 'user2')

# সব ইউজার পাওয়া
users = r.smembers('online_users')

# চেক করা
is_online = r.sismember('online_users', 'user1')
```

### ৫. Sorted Sets (র‍্যাঙ্কিং সিস্টেম)
```python
# স্কোর সহ আইটেম যুক্ত
r.zadd('leaderboard', {'player1': 100, 'player2': 200})

# টপ প্লেয়ার পাওয়া
top_players = r.zrevrange('leaderboard', 0, 9, withscores=True)
```

## Django Redis অ্যাডভান্সড ব্যবহার

### ১. ডাটাবেস ক্যাশিং প্যাটার্ন
```python
class CachedModelManager(models.Manager):
    def get_cached(self, pk):
        cache_key = f'{self.model._meta.model_name}_{pk}'
        data = cache.get(cache_key)
        
        if not data:
            data = self.get(pk=pk)
            cache.set(cache_key, data, 3600)
        
        return data

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    objects = CachedModelManager()

# ব্যবহার
product = Product.objects.get_cached(1)
```

### ২. ফ্র্যাগমেন্ট ক্যাশিং
```python
from django.core.cache import cache
from django.template.loader import render_to_string

def cached_menu(request):
    cache_key = 'main_menu'
    menu_html = cache.get(cache_key)
    
    if not menu_html:
        menu_items = Menu.objects.all()
        menu_html = render_to_string('menu.html', {'items': menu_items})
        cache.set(cache_key, menu_html, 3600)
    
    return menu_html
```

### ৩. Redis Pub/Sub (রিয়েল-টাইম নোটিফিকেশন)
```python
# publisher.py
import redis
import json

r = redis.Redis()

def send_notification(user_id, message):
    data = {'user_id': user_id, 'message': message}
    r.publish('notifications', json.dumps(data))

# consumer.py (সেলারি টাস্ক)
@shared_task
def notification_consumer():
    r = redis.Redis()
    pubsub = r.pubsub()
    pubsub.subscribe('notifications')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            # নোটিফিকেশন প্রসেস করুন
```

## পারফরম্যান্স অপ্টিমাইজেশন

### ১. Redis ক্যাশিং স্ট্র্যাটেজি
```python
class CacheStrategy:
    @staticmethod
    def cache_or_fetch(key, fetch_func, timeout=300):
        """ক্যাশে থেকে ডেটা আনুন অথবা ফাংশন থেকে ফেচ করুন"""
        data = cache.get(key)
        if data is None:
            data = fetch_func()
            cache.set(key, data, timeout)
        return data
    
    @staticmethod
    def write_through(key, value, save_func, timeout=300):
        """ডাটাবেসে সেভ করে ক্যাশেও সেভ করুন"""
        save_func()  # ডাটাবেসে সেভ
        cache.set(key, value, timeout)
```

### ২. ব্যাচ অপারেশন
```python
def get_multiple_users(user_ids):
    # একাধিক key একসাথে fetch করা
    keys = [f'user:{id}' for id in user_ids]
    users = cache.get_many(keys)
    
    missing_ids = []
    result = []
    
    for user_id in user_ids:
        key = f'user:{user_id}'
        if key in users:
            result.append(users[key])
        else:
            missing_ids.append(user_id)
    
    if missing_ids:
        # ডাটাবেস থেকে মিসিং ডেটা আনুন
        db_users = User.objects.filter(id__in=missing_ids)
        for user in db_users:
            key = f'user:{user.id}'
            cache.set(key, user, 3600)
            result.append(user)
    
    return result
```

## মনিটরিং ও মেইনটেন্যান্স

### Redis মনিটরিং কমান্ড:
```bash
# Redis তথ্য
redis-cli info

# ক্যাশে হিট রেট চেক
redis-cli info stats | grep keyspace_hits
redis-cli info stats | grep keyspace_misses

# মেমরি ব্যবহার
redis-cli info memory

# ক্লায়েন্ট কানেকশন
redis-cli info clients
```

### Django ডিবাগ টুল:
```python
# Django Shell থেকে Redis টেস্ট
python manage.py shell

import django.core.cache as cache
# ক্যাশে টেস্ট
cache.set('test', 'value', 30)
cache.get('test')
```

## সিকিউরিটি বেস্ট প্র্যাকটিস

### ১. Redis পাসওয়ার্ড সেটআপ:
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://:yourpassword@localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### ২. SSL/TLS কনফিগারেশন:
```python
LOCATION = 'rediss://localhost:6379/0'  # SSL/TLS
```

## সাধারণ সমস্যা ও সমাধান

### ১. ক্যাশে ইনভ্যালিডেশন সমস্যা:
```python
def update_user(user_id, data):
    # ইউজার আপডেট
    user = User.objects.get(id=user_id)
    user.name = data['name']
    user.save()
    
    # ক্যাশে ইনভ্যালিডেট করুন
    cache_key = f'user:{user_id}'
    cache.delete(cache_key)
```

### ২. ক্যাশে স্ট্যাম্পেডি সমস্যা (Cache Stampeding):
```python
import time
from django.core.cache import cache

def get_data_with_lock(key, fetch_func, timeout=300):
    """Lock ব্যবহার করে cache stampeding প্রতিরোধ"""
    data = cache.get(key)
    
    if data is None:
        lock_key = f'{key}:lock'
        # Lock পাবার চেষ্টা করুন
        if cache.add(lock_key, '1', 10):  # 10 সেকেন্ড lock
            try:
                data = fetch_func()
                cache.set(key, data, timeout)
            finally:
                cache.delete(lock_key)
        else:
            # অন্য প্রসেস ডেটা ফেচ করছে, অপেক্ষা করুন
            time.sleep(0.1)
            data = cache.get(key)
    
    return data
```

## প্রজেক্ট আর্কিটেকচার উদাহরণ

### E-commerce সাইট Redis ব্যবহার:
```python
# ecommerce/caching.py
from django.core.cache import cache
import json

class EcommerceCache:
    @staticmethod
    def get_product(product_id):
        key = f'product:{product_id}'
        return cache.get(key)
    
    @staticmethod
    def cache_product(product):
        key = f'product:{product.id}'
        cache.set(key, product, 3600)  # 1 hour
        
        # ক্যাটাগরি অনুযায়ীও ক্যাশে করুন
        cat_key = f'category:{product.category_id}:products'
        cache.delete(cat_key)
    
    @staticmethod
    def get_cart(user_id):
        key = f'cart:{user_id}'
        cart_data = cache.get(key)
        return json.loads(cart_data) if cart_data else {}
    
    @staticmethod
    def update_cart(user_id, cart_data):
        key = f'cart:{user_id}'
        cache.set(key, json.dumps(cart_data), 86400)  # 24 hours
    
    @staticmethod
    def get_homepage_data():
        key = 'homepage_data'
        data = cache.get(key)
        
        if not data:
            from .models import Product, Category
            data = {
                'featured_products': list(Product.objects.filter(featured=True)[:10]),
                'categories': list(Category.objects.all()),
                'top_sellers': list(Product.objects.order_by('-sold_count')[:10])
            }
            cache.set(key, data, 1800)  # 30 minutes
        
        return data
```

## লার্নিং রিসোর্স

### বাংলা রিসোর্স:
1. **ডjango অফিসিয়াল ডকুমেন্টেশন** (বাংলা অনুবাদ পাওয়া যায়)
2. **Redis ডকুমেন্টেশন** (বেসিক টিউটোরিয়াল)
3. **YouTube বাংলা টিউটোরিয়াল**: Django + Redis

### প্র্যাকটিস প্রোজেক্ট:
1. **ব্লগ সাইট**: Redis ক্যাশিং, সেশন ম্যানেজমেন্ট
2. **ই-কমার্স**: প্রডাক্ট ক্যাশিং, কার্ট ম্যানেজমেন্ট
3. **রিয়েল-টাইম চ্যাট**: Redis Pub/Sub ব্যবহার করে
4. **API সার্ভিস**: রেট লিমিটিং, ক্যাশিং

## উপসংহার

Redis Django অ্যাপ্লিকেশনের পারফরম্যান্স উন্নত করার শক্তিশালী টুল। বিগিনার হিসেবে ক্যাশিং দিয়ে শুরু করে আস্তে আস্তে অ্যাডভান্সড ব্যবহার শিখতে হবে। মনে রাখবেন, Redis ইন-মেমরি ডাটাবেস, তাই গুরুত্বপূর্ণ ডেটা সবসময় প্রাইমারি ডাটাবেসে স্টোর করতে হবে।

**গুরুত্বপূর্ণ টিপস**:
1. প্রোডাকশনে সর্বদা Redis পাসওয়ার্ড প্রটেক্টেড রাখুন
2. মেমরি মনিটরিং করুন রেগুলারলি
3. ক্যাশে টিটিএল (Time To Live) সেট করুন
4. ডাটাবেসের backup পরিকল্পনা রাখুন

শুভকামনা!