# Nginx বিস্তারিত গাইড: বিগিনার থেকে অ্যাডভান্সড

## ১. Nginx কি? (What is Nginx?)
Nginx (এনজিনএক্স) একটি ওপেন-সোর্স, হাই-পারফরম্যান্স ওয়েব সার্ভার, রিভার্স প্রোক্সি, লোড ব্যালেন্সার এবং HTTP ক্যাশে সার্ভার। এটি ২০০৪ সালে Igor Sysoev তৈরি করেন।

### কেন Nginx ব্যবহার করবেন?
- **দ্রুত গতি**: ইভেন্ট-ড্রিভেন আর্কিটেকচার
- **কম রিসোর্স ব্যবহার**: কম মেমরি খরচ
- **স্কেলেবিলিটি**: সহজে হ্যান্ডেল করতে পারে হাজারো কানেকশন
- **বহুমুখীতা**: একসাথে Multiple ভূমিকা পালন করতে পারে

## ২. ইনস্টলেশন (Installation)

### Ubuntu/Debian এ ইনস্টলেশন:
```bash
sudo apt update
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### CentOS/RHEL এ ইনস্টলেশন:
```bash
sudo yum install epel-release
sudo yum install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## ৩. বেসিক কনফিগারেশন (Basic Configuration)

### Nginx ডিরেক্টরি স্ট্রাকচার:
```
/etc/nginx/
├── nginx.conf          # মেইন কনফিগারেশন ফাইল
├── sites-available/    # সব সাইটের কনফিগারেশন
├── sites-enabled/      # একটিভ সাইটের কনফিগারেশন
├── conf.d/             # অ্যাডিশনাল কনফিগারেশন
└── snippets/           # রিউজেবল কনফিগারেশন স্নিপেট
```

### বেসিক ভার্চুয়াল হোস্ট কনফিগারেশন:
```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    
    root /var/www/example.com;
    index index.html index.htm;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

## ৪. গুরুত্বপূর্ণ ডিরেক্টিভস (Important Directives)

### HTTP ব্লক:
```nginx
http {
    # মৌলিক সেটিংস
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # MIME টাইপ
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # লগিং
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # ভার্চুয়াল হোস্ট
    include /etc/nginx/sites-enabled/*;
}
```

### ইভেন্ট ব্লক:
```nginx
events {
    worker_connections 1024;
    multi_accept on;
    use epoll; # Linux এর জন্য
}
```

## ৫. লোকেশন ব্লক (Location Blocks)

```nginx
location = /exact {
    # শুধুমাত্র /exact এর জন্য ম্যাচ হবে
}

location ^~ /static {
    # /static দিয়ে শুরু হলে
}

location ~ \.php$ {
    # .php দিয়ে শেষ হলে (case-sensitive)
}

location ~* \.(jpg|jpeg|png)$ {
    # ছবির ফাইলগুলো (case-insensitive)
}

location / {
    # ডিফল্ট লোকেশন
}
```

## ৬. স্ট্যাটিক কন্টেন্ট সার্ভিং (Static Content)

```nginx
server {
    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads/ {
        alias /var/www/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

## ৭. PHP প্রসেসিং (PHP Processing with PHP-FPM)

```nginx
server {
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

## ৮. রিভার্স প্রোক্সি সেটআপ (Reverse Proxy Setup)

```nginx
server {
    listen 80;
    server_name app.example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## ৯. লোড ব্যালেন্সিং (Load Balancing)

```nginx
upstream backend_servers {
    server backend1.example.com weight=3;
    server backend2.example.com;
    server backend3.example.com backup;
    
    # লোড ব্যালেন্সিং মেথড
    # least_conn;    # কম কানেকশন আছে এমন সার্ভারে পাঠাবে
    # ip_hash;      # একই ক্লায়েন্ট সবসময় একই সার্ভারে যাবে
}

server {
    location / {
        proxy_pass http://backend_servers;
    }
}
```

## ১০. SSL/TLS কনফিগারেশন (SSL/TLS Configuration)

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
    
    # SSL সেটিংস
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

## ১১. ক্যাশিং কনফিগারেশন (Caching Configuration)

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m 
                 max_size=1g inactive=60m use_temp_path=off;

server {
    location / {
        proxy_cache my_cache;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
        add_header X-Cache-Status $upstream_cache_status;
        proxy_pass http://backend;
    }
}
```

## ১২. সিকিউরিটি সেটিংস (Security Settings)

```nginx
# ক্লিকজ্যাকিং থেকে প্রোটেকশন
add_header X-Frame-Options "SAMEORIGIN" always;

# XSS প্রোটেকশন
add_header X-XSS-Protection "1; mode=block" always;

# Content Type স্নিফিং থেকে প্রোটেকশন
add_header X-Content-Type-Options "nosniff" always;

# রেফারার পলিসি
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# ফাইল সাইজ লিমিট
client_max_body_size 10M;

# রেট লিমিটিং
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

location /login {
    limit_req zone=one burst=5;
}
```

## ১৩. পারফরম্যান্স অপটিমাইজেশন (Performance Optimization)

```nginx
http {
    # Gzip কম্প্রেশন
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml application/json 
               application/javascript application/xml+rss;
    
    # Static ফাইল ক্যাশিং
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    # কানেকশন অপটিমাইজেশন
    keepalive_timeout 30;
    keepalive_requests 100;
}
```

## ১৪. মনিটরিং ও লগিং (Monitoring & Logging)

```nginx
# কাস্টম লগ ফরম্যাট
log_format custom '$remote_addr - $remote_user [$time_local] '
                  '"$request" $status $body_bytes_sent '
                  '"$http_referer" "$http_user_agent" '
                  '$request_time $upstream_response_time';

access_log /var/log/nginx/access.log custom;

# স্ট্যাটাস পেজ (Nginx Plus)
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

## ১৫. প্রবলেম সলভিং (Troubleshooting)

### সাধারণ সমস্যা ও সমাধান:

1. **কনফিগারেশন চেক**:
```bash
sudo nginx -t
```

2. **Nginx রিস্টার্ট**:
```bash
sudo systemctl restart nginx
# অথবা
sudo nginx -s reload
```

3. **লগ চেক**:
```bash
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

4. **পোর্ট চেক**:
```bash
sudo netstat -tulpn | grep nginx
```

## ১৬. অ্যাডভান্সড কনফিগারেশন

### মাইক্রোসার্ভিস আর্কিটেকচার:
```nginx
# API Gateway হিসেবে Nginx
upstream user_service {
    server 192.168.1.10:8001;
}

upstream product_service {
    server 192.168.1.11:8002;
}

upstream order_service {
    server 192.168.1.12:8003;
}

server {
    location /api/users {
        rewrite ^/api/users/(.*) /$1 break;
        proxy_pass http://user_service;
    }
    
    location /api/products {
        rewrite ^/api/products/(.*) /$1 break;
        proxy_pass http://product_service;
    }
}
```

### WebSocket সাপোর্ট:
```nginx
location /ws/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_set_header Host $host;
}
```

## ১৭. বেস্ট প্র্যাকটিসেস (Best Practices)

1. **নিয়মিত আপডেট রাখুন**
2. **অনাবশ্যক মডিউল disable করুন**
3. **Production এ SELinux/AppArmor ব্যবহার করুন**
4. **কনফিগারেশন ভার্সন কন্ট্রোল করুন**
5. **নিয়মিত লগ মনিটর করুন**
6. **Rate limiting ইমপ্লিমেন্ট করুন**
7. **SSL/TLS প্রোপারলি কনফিগার করুন**

## ১৮. লার্নিং রিসোর্সেস (Learning Resources)

### বাংলা রিসোর্স:
1. Nginx বাংলা টিউটোরিয়াল - মুহাম্মদ মুনতাকিম
2. ক্লাউডওয়াইজ - বাংলা ব্লগ

### ইংরেজি রিসোর্স:
1. [Nginx Official Documentation](https://nginx.org/en/docs/)
2. [DigitalOcean Nginx Tutorials](https://www.digitalocean.com/community/tags/nginx)
3. [Nginx Admin's Handbook](https://github.com/trimstray/nginx-admins-handbook)

### প্র্যাকটিস করার স্টেপ:
1. লোকাল মেশিনে Nginx ইন্সটল করুন
2. একটি স্ট্যাটিক ওয়েবসাইট হোস্ট করুন
3. PHP অ্যাপ্লিকেশন সার্ভ করুন
4. রিভার্স প্রোক্সি সেটআপ করুন
5. লোড ব্যালেন্সিং ইমপ্লিমেন্ট করুন
6. SSL/TLS কনফিগার করুন

## উপসংহার
Nginx শেখা শুরু করতে বেসিক কনফিগারেশন দিয়ে শুরু করুন, ধীরে ধীরে অ্যাডভান্সড টপিকগুলো শিখুন। রিয়েল-ওয়ার্ল্ড প্রোজেক্টে প্রয়োগ করার মাধ্যমে অভিজ্ঞতা অর্জন করুন। সিকিউরিটি ও পারফরম্যান্স সবসময় priority দিন।