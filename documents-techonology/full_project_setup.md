# **Production-Ready Authentication System in Django**

## **Project Overview**
We'll build a comprehensive authentication system with industry standards, covering everything from development to production deployment.

## **Project Structure**
```
auth_project/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── tests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_models.py
│   │   │   │   ├── test_views.py
│   │   │   │   ├── test_serializers.py
│   │   │   │   └── test_tasks.py
│   │   │   ├── urls.py
│   │   │   ├── utils.py
│   │   │   ├── validators.py
│   │   │   └── views.py
│   │   └── core/
│   ├── templates/
│   └── static/
├── nginx/
│   ├── nginx.conf
│   └── nginx.prod.conf
├── scripts/
│   ├── entrypoint.sh
│   ├── start-celery.sh
│   └── start-celery-beat.sh
├── tests/
│   └── conftest.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── Makefile
└── manage.py
```

## **Step 1: Setup Environment**

### **1.1 Create Project Structure**
```bash
mkdir -p auth_project/{src/apps/{accounts,core},requirements,tests,scripts,nginx,.github/workflows}
cd auth_project
```

### **1.2 Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### **1.3 Requirements Files**

**requirements/base.txt**
```txt
Django==4.2.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.2.0
celery==5.3.1
redis==4.6.0
django-redis==5.3.0
psycopg2-binary==2.9.6
python-dotenv==1.0.0
drf-yasg==1.21.5
django-rest-passwordreset==1.3.1
django-allauth==0.54.0
django-cleanup==8.0.0
django-extensions==3.2.3
whitenoise==6.5.0
gunicorn==21.2.0
django-storages==1.14.0
boto3==1.28.0
Pillow==10.0.0
python-decouple==3.8
sentry-sdk==1.30.0
```

**requirements/development.txt**
```txt
-r base.txt
ipython==8.14.0
django-debug-toolbar==4.1.0
pytest==7.4.0
pytest-django==4.5.2
pytest-cov==4.1.0
factory-boy==3.3.0
faker==19.6.2
flake8==6.0.0
black==23.7.0
isort==5.12.0
coverage==7.3.0
freezegun==1.2.2
```

**requirements/production.txt**
```txt
-r base.txt
# Additional production-only packages if needed
```

## **Step 2: Django Project Setup**

### **2.1 Initialize Django Project**
```bash
cd src
django-admin startproject config .
cd ..
```

### **2.2 Create Custom User Model**

**src/apps/accounts/models.py**
```python
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    
    # Auth fields
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email.'),
    )
    
    # Timestamps
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Social login IDs
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Email preferences
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f"Profile of {self.user.email}"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('login history')
        verbose_name_plural = _('login histories')
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', 'login_time']),
        ]


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['token', 'is_used', 'expires_at']),
        ]
```

### **2.3 Settings Configuration**

**src/config/settings/base.py**
```python
import os
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_cleanup.apps.CleanupConfig',
    'django_extensions',
    'storages',
    
    # Local apps
    'apps.accounts',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='auth_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Email configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@yourapp.com')

# Django Allauth
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=False, cast=bool)

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        },
        'KEY_PREFIX': 'auth',
    }
}

# Cache timeout
CACHE_TTL = 60 * 15

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/errors.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.accounts': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Sentry
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

# AWS S3 (for production)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

## **Step 3: Create Serializers**

**src/apps/accounts/serializers.py**
```python
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User, UserProfile, LoginHistory
from .validators import validate_password_strength
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password_strength],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'confirm_password')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """
        Validate email format and uniqueness.
        """
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError(_("Enter a valid email address."))

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        
        return value.lower()

    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        
        return attrs

    def create(self, validated_data):
        """
        Create user with hashed password.
        """
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_verified=False
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    ip_address = serializers.IPAddressField(write_only=True, required=False)
    user_agent = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(_("Must include email and password."))

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(_("Invalid email or password."))

        if not user.is_active:
            raise serializers.ValidationError(_("User account is disabled."))

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 
            'is_active', 'is_verified', 'date_joined',
            'last_login', 'phone_number', 'avatar', 'profile'
        )
        read_only_fields = ('id', 'email', 'date_joined', 'last_login')

    def get_profile(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile:
            return UserProfileSerializer(profile).data
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password_strength]
    )
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is incorrect."))
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError(
                {"new_password": _("New password must be different from old password.")}
            )
        
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User with this email does not exist."))
        
        if not user.is_active:
            raise serializers.ValidationError(_("User account is disabled."))
        
        return value


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password_strength]
    )
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        
        return attrs


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = '__all__'
        read_only_fields = ('user', 'login_time')


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'avatar')
```

## **Step 4: Create Views and API Endpoints**

**src/apps/accounts/views.py**
```python
import logging
from django.core.cache import cache
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, LoginHistory, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    VerifyEmailSerializer, LoginHistorySerializer, UpdateProfileSerializer
)
from .utils import (
    generate_verification_token, send_verification_email,
    send_password_reset_email, verify_token, track_login_attempt
)
from .tasks import send_welcome_email, send_password_change_notification

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'registration'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate verification token
        token = generate_verification_token(user)
        
        # Send verification email via Celery
        send_verification_email.delay(user.email, token)
        
        # Send welcome email via Celery
        send_welcome_email.delay(user.id)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Track registration
        logger.info(f"User registered: {user.email}")
        
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Registration successful. Please verify your email.'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    Login user and return JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer
    throttle_scope = 'login'

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        ip_address = serializer.validated_data.get('ip_address', 
                    request.META.get('REMOTE_ADDR', ''))
        user_agent = serializer.validated_data.get('user_agent',
                    request.META.get('HTTP_USER_AGENT', ''))
        
        # Track login attempt
        track_login_attempt(user, ip_address, user_agent, True)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Cache user data for quick access
        cache_key = f'user_{user.id}_data'
        cache.set(cache_key, {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_verified': user.is_verified
        }, timeout=300)  # 5 minutes
        
        logger.info(f"User logged in: {user.email} from {ip_address}")
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })


class UserLogoutView(APIView):
    """
    Logout user by blacklisting refresh token
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Clear user cache
            cache.delete(f'user_{request.user.id}_data')
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    """
    Update user profile
    """
    serializer_class = UpdateProfileSerializer
    permission_class = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        super().perform_update(serializer)
        # Clear cache
        cache.delete(f'user_{self.request.user.id}_data')


class ChangePasswordView(APIView):
    """
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = 'password_change'

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Update profile
        if hasattr(user, 'profile'):
            user.profile.last_password_change = timezone.now()
            user.profile.save()
        
        # Send notification via Celery
        send_password_change_notification.delay(user.id)
        
        # Clear all user sessions
        user.auth_token_set.all().delete()
        
        logger.info(f"Password changed for user: {user.email}")
        
        return Response({'message': 'Password changed successfully'})


class ForgotPasswordView(APIView):
    """
    Request password reset
    """
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'forgot_password'

    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email__iexact=email)
        
        # Create password reset token
        token = PasswordResetToken.objects.create(
            user=user,
            token=generate_verification_token(user),
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        # Send reset email via Celery
        send_password_reset_email.delay(user.email, token.token)
        
        logger.info(f"Password reset requested for: {user.email}")
        
        return Response({
            'message': 'Password reset email sent. Check your inbox.'
        })


class ResetPasswordView(APIView):
    """
    Reset password with token
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Verify token
        reset_token = verify_token(token, PasswordResetToken)
        
        if not reset_token or reset_token.is_used:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.save()
        
        # Clear all user sessions
        user.auth_token_set.all().delete()
        
        logger.info(f"Password reset for user: {user.email}")
        
        return Response({'message': 'Password reset successful'})


class VerifyEmailView(APIView):
    """
    Verify email with token
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=VerifyEmailSerializer)
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        
        # In production, you'd have a token verification mechanism
        # This is a simplified version
        try:
            user = User.objects.get(id=token)  # Simplified
            user.is_verified = True
            user.save()
            
            logger.info(f"Email verified for user: {user.email}")
            
            return Response({'message': 'Email verified successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginHistoryView(generics.ListAPIView):
    """
    Get user login history
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view with additional logging
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        logger.info(f"Token refreshed for user")
        return response


class DeleteAccountView(APIView):
    """
    Delete user account
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        email = user.email
        
        # Soft delete or mark as inactive
        user.is_active = False
        user.save()
        
        # Log deletion
        logger.info(f"Account deleted for user: {email}")
        
        return Response({'message': 'Account deleted successfully'})
```

## **Step 5: Create Celery Tasks**

**src/apps/accounts/tasks.py**
```python
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.cache import cache
from .models import User

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_verification_email(self, email, token):
    """
    Send email verification link
    """
    try:
        subject = 'Verify Your Email Address'
        html_message = render_to_string('accounts/email_verification.html', {
            'verification_link': f'{settings.FRONTEND_URL}/verify-email/{token}',
            'token': token,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        self.retry(countdown=60 * 2 ** self.request.retries)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, email, token):
    """
    Send password reset email
    """
    try:
        subject = 'Reset Your Password'
        html_message = render_to_string('accounts/password_reset.html', {
            'reset_link': f'{settings.FRONTEND_URL}/reset-password/{token}',
            'token': token,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        self.retry(countdown=60 * 2 ** self.request.retries)


@shared_task
def send_welcome_email(user_id):
    """
    Send welcome email to new user
    """
    try:
        user = User.objects.get(id=user_id)
        subject = 'Welcome to Our Platform!'
        html_message = render_to_string('accounts/welcome_email.html', {
            'user': user,
            'login_link': f'{settings.FRONTEND_URL}/login',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")


@shared_task
def send_password_change_notification(user_id):
    """
    Send notification when password is changed
    """
    try:
        user = User.objects.get(id=user_id)
        subject = 'Password Changed Successfully'
        html_message = render_to_string('accounts/password_change_notification.html', {
            'user': user,
            'support_email': settings.SUPPORT_EMAIL,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password change notification sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send password change notification: {str(e)}")


@shared_task
def clean_expired_tokens():
    """
    Clean expired password reset and verification tokens
    """
    from django.utils import timezone
    from .models import PasswordResetToken
    
    expired_tokens = PasswordResetToken.objects.filter(
        expires_at__lt=timezone.now(),
        is_used=False
    ).delete()
    
    logger.info(f"Cleaned {expired_tokens[0]} expired tokens")


@shared_task
def update_user_cache(user_id):
    """
    Update user data in cache
    """
    try:
        user = User.objects.get(id=user_id)
        cache_key = f'user_{user_id}_data'
        cache.set(cache_key, {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_verified': user.is_verified
        }, timeout=3600)  # 1 hour
        
    except Exception as e:
        logger.error(f"Failed to update cache for user {user_id}: {str(e)}")
```

## **Step 6: Create Utility Functions and Validators**

**src/apps/accounts/utils.py**
```python
import uuid
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
import jwt
from .models import LoginHistory


def generate_verification_token(user):
    """
    Generate a secure verification token
    """
    payload = {
        'user_id': str(user.id),
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'type': 'verification'
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token, token_model):
    """
    Verify a token from given model
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        token_obj = token_model.objects.get(
            token=token,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        return token_obj
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, token_model.DoesNotExist):
        return None


def track_login_attempt(user, ip_address, user_agent, success, failure_reason=None):
    """
    Track user login attempts
    """
    LoginHistory.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        failure_reason=failure_reason
    )
    
    # Rate limiting logic
    if not success:
        cache_key = f'failed_login_{ip_address}'
        failed_attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, failed_attempts, timeout=3600)  # 1 hour
        
        if failed_attempts >= 5:
            # Implement account lockout or CAPTCHA
            pass


def validate_password_strength(password):
    """
    Validate password strength
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit.")
    
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for char in password):
        errors.append("Password must contain at least one special character.")
    
    return errors
```

**src/apps/accounts/validators.py**
```python
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_password_strength(value):
    """
    Django validator for password strength
    """
    if len(value) < 8:
        raise ValidationError(
            _("Password must be at least 8 characters long."),
            code='password_too_short'
        )
    
    if not re.search(r'\d', value):
        raise ValidationError(
            _("Password must contain at least one digit."),
            code='password_no_digit'
        )
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(
            _("Password must contain at least one uppercase letter."),
            code='password_no_upper'
        )
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(
            _("Password must contain at least one lowercase letter."),
            code='password_no_lower'
        )
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?`~]', value):
        raise ValidationError(
            _("Password must contain at least one special character."),
            code='password_no_special'
        )
```

## **Step 7: Create URL Routes**

**src/apps/accounts/urls.py**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # Password Management
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    # Email Verification
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    
    # Profile Management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('login-history/', views.LoginHistoryView.as_view(), name='login_history'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    
    # Include router URLs
    path('', include(router.urls)),
]
```

**src/config/urls.py**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Authentication API",
        default_version='v1',
        description="Production-ready authentication system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.core.urls')),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
```

## **Step 8: Docker Configuration**

**docker-compose.yml**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000"
    volumes:
      - ./src:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DEBUG=0
      - DATABASE_URL=postgres://postgres:postgres@db:5432/auth_db
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery:
    build: .
    command: celery -A config worker --loglevel=info
    volumes:
      - ./src:/app
    environment:
      - DEBUG=0
      - DATABASE_URL=postgres://postgres:postgres@db:5432/auth_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      - web

  celery-beat:
    build: .
    command: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./src:/app
    environment:
      - DEBUG=0
      - DATABASE_URL=postgres://postgres:postgres@db:5432/auth_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

**docker-compose.prod.yml**
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web

  web:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    environment:
      - DEBUG=0
      - SECURE_SSL_REDIRECT=1
      - SECURE_HSTS_SECONDS=31536000
      - SECURE_HSTS_INCLUDE_SUBDOMAINS=1
      - SECURE_HSTS_PRELOAD=1
      - SESSION_COOKIE_SECURE=1
      - CSRF_COOKIE_SECURE=1

  celery:
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  celery-beat:
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
```

**Dockerfile**
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt .
RUN pip install --upgrade pip && \
    pip install -r production.txt

# Copy project
COPY src/ /app/

# Create non-root user
RUN addgroup --system --gid 1001 django && \
    adduser --system --uid 1001 --gid 1001 django && \
    chown -R django:django /app

USER django

# Run entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

## **Step 9: Test Cases**

**src/apps/accounts/tests/test_models.py**
```python
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import User, UserProfile, LoginHistory

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'Test@123456',
            'first_name': 'John',
            'last_name': 'Doe'
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('Test@123456'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='Test@123456')

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='Admin@123456'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_user_str_method(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')

    def test_user_full_name(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, 'John Doe')

    def test_user_profile_creation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)

    def test_user_profile_str_method(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user.profile), f"Profile of {user.email}")


class LoginHistoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Test@123456'
        )

    def test_login_history_creation(self):
        login_history = LoginHistory.objects.create(
            user=self.user,
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            success=True
        )
        self.assertEqual(login_history.user, self.user)
        self.assertEqual(login_history.ip_address, '127.0.0.1')
        self.assertTrue(login_history.success)
```

**src/apps/accounts/tests/test_views.py**
```python
import json
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import User


class AuthenticationAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        
        self.user_data = {
            'email': 'test@example.com',
            'password': 'Test@123456',
            'confirm_password': 'Test@123456',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        self.login_data = {
            'email': 'test@example.com',
            'password': 'Test@123456'
        }

    def test_user_registration_success(self):
        response = self.client.post(
            self.register_url,
            data=self.user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_user_registration_with_existing_email(self):
        # Create user first
        User.objects.create_user(
            email='test@example.com',
            password='Test@123456'
        )
        
        response = self.client.post(
            self.register_url,
            data=self.user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_with_weak_password(self):
        weak_password_data = self.user_data.copy()
        weak_password_data['password'] = '123'
        weak_password_data['confirm_password'] = '123'
        
        response = self.client.post(
            self.register_url,
            data=weak_password_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login_success(self):
        # Create user first
        User.objects.create_user(
            email='test@example.com',
            password='Test@123456'
        )
        
        response = self.client.post(
            self.login_url,
            data=self.login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_user_login_with_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            data={
                'email': 'wrong@example.com',
                'password': 'Wrong@123'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout(self):
        # Create and login user
        user = User.objects.create_user(
            email='test@example.com',
            password='Test@123456'
        )
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )
        
        response = self.client.post(
            self.logout_url,
            data={'refresh': str(refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_profile_authenticated(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='Test@123456'
        )
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeAPITestCase(APITestCase):
    def setUp(self):
        self.change_password_url = reverse('change_password')
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Old@123456'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

    def test_change_password_success(self):
        data = {
            'old_password': 'Old@123456',
            'new_password': 'New@123456',
            'confirm_password': 'New@123456'
        }
        
        response = self.client.post(
            self.change_password_url,
            data=data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('New@123456'))

    def test_change_password_with_wrong_old_password(self):
        data = {
            'old_password': 'Wrong@123456',
            'new_password': 'New@123456',
            'confirm_password': 'New@123456'
        }
        
        response = self.client.post(
            self.change_password_url,
            data=data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IntegrationTest(APITestCase):
    def test_full_authentication_flow(self):
        # 1. Register
        register_data = {
            'email': 'newuser@example.com',
            'password': 'Test@123456',
            'confirm_password': 'Test@123456',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        
        register_response = self.client.post(
            reverse('register'),
            data=register_data,
            format='json'
        )
        
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # 2. Login
        login_response = self.client.post(
            reverse('login'),
            data={
                'email': 'newuser@example.com',
                'password': 'Test@123456'
            },
            format='json'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        access_token = login_response.data['access']
        
        # 3. Get Profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(reverse('profile'))
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # 4. Logout
        logout_response = self.client.post(
            reverse('logout'),
            data={'refresh': login_response.data['refresh']},
            format='json'
        )
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # 5. Try accessing profile after logout
        profile_response_after_logout = self.client.get(reverse('profile'))
        self.assertEqual(profile_response_after_logout.status_code, status.HTTP_401_UNAUTHORIZED)
```

## **Step 10: Production Configuration**

### **10.1 Nginx Configuration**

**nginx/nginx.prod.conf**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/yourdomain.com.crt;
        ssl_certificate_key /etc/nginx/ssl/yourdomain.com.key;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self';" always;
        
        location / {
            proxy_pass http://django;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Host $host;
            proxy_redirect off;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### **10.2 Celery Configuration**

**src/config/celery.py**
```python
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'clean-expired-tokens-every-day': {
        'task': 'apps.accounts.tasks.clean_expired_tokens',
        'schedule': crontab(hour=0, minute=0),
    },
    'send-email-reports-weekly': {
        'task': 'apps.accounts.tasks.send_weekly_report',
        'schedule': crontab(day_of_week=0, hour=8, minute=0),  # Sunday 8 AM
    },
}

app.conf.timezone = 'UTC'
```

**src/config/__init__.py**
```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### **10.3 Deployment Scripts**

**scripts/entrypoint.sh**
```bash
#!/bin/sh

set -e

# Wait for database
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database started"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "Redis started"

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if doesn't exist
echo "Creating superuser..."
python manage.py createsuperuser --noinput --email $DJANGO_SUPERUSER_EMAIL || true

# Start server
echo "Starting server..."
exec "$@"
```

**scripts/start-celery.sh**
```bash
#!/bin/bash

set -e

# Wait for dependencies
sleep 10

exec celery -A config worker --loglevel=info --concurrency=4
```

## **Step 11: CI/CD Pipeline**

**.github/workflows/ci-cd.yml**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  DOCKER_IMAGE: your-registry/auth-app

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements/development.txt
    
    - name: Run migrations
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
      run: |
        cd src
        python manage.py migrate
    
    - name: Run tests with coverage
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
      run: |
        cd src
        coverage run -m pytest
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
    
    - name: Run security check
      run: |
        pip install bandit
        bandit -r src -f json -o bandit-report.json
    
    - name: Lint code
      run: |
        pip install flake8 black isort
        black --check src
        isort --check-only src
        flake8 src

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ env.DOCKER_IMAGE }}:latest

  deploy:
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      uses: appleboy/ssh-action@v0.1.4
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.PRODUCTION_SSH_KEY }}
        script: |
          cd /opt/auth-app
          docker-compose pull
          docker-compose down
          docker-compose up -d
          docker system prune -f
```

## **Step 12: Monitoring and Logging**

### **12.1 Add Monitoring Endpoints**

**src/apps/core/views.py**
```python
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from django.db import connection
import redis
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(View):
    def get(self, request):
        """
        Health check endpoint for monitoring
        """
        health_status = {
            'status': 'healthy',
            'services': {}
        }
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['services']['database'] = 'healthy'
        except Exception as e:
            health_status['services']['database'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
            logger.error(f"Database health check failed: {e}")
        
        # Check Redis
        try:
            r = redis.from_url(cache.client.get_client().connection_pool.connection_kwargs['url'])
            r.ping()
            health_status['services']['redis'] = 'healthy'
        except Exception as e:
            health_status['services']['redis'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
            logger.error(f"Redis health check failed: {e}")
        
        return JsonResponse(health_status, status=200 if health_status['status'] == 'healthy' else 503)


class MetricsView(View):
    def get(self, request):
        """
        Metrics endpoint for monitoring
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        metrics = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
        }
        
        return JsonResponse(metrics)
```

### **12.2 Create Middleware for Request Logging**

**src/apps/core/middleware.py**
```python
import time
import json
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': duration,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                'ip': request.META.get('REMOTE_ADDR'),
            }
            
            if duration > 1:  # Log slow requests
                logger.warning(f"Slow request detected: {json.dumps(log_data)}")
            
            if response.status_code >= 400:
                logger.error(f"Error response: {json.dumps(log_data)}")
            
            logger.info(f"Request processed: {json.dumps(log_data)}")
        
        return response
```

## **Step 13: Security Enhancements**

### **13.1 Custom Authentication Backend**

**src/apps/accounts/authentication.py**
```python
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Custom authentication with rate limiting and logging
        """
        if email is None:
            email = kwargs.get(User.USERNAME_FIELD)
        
        if email is None or password is None:
            return None
        
        # Rate limiting check
        ip_address = request.META.get('REMOTE_ADDR') if request else 'unknown'
        cache_key = f'failed_login_{ip_address}'
        failed_attempts = cache.get(cache_key, 0)
        
        if failed_attempts >= 10:
            logger.warning(f"Too many failed attempts from IP: {ip_address}")
            return None
        
        try:
            # Case-insensitive email lookup
            user = User.objects.get(email__iexact=email)
            
            if user.check_password(password):
                if not user.is_active:
                    logger.warning(f"Inactive user attempted login: {email}")
                    return None
                
                # Reset failed attempts on successful login
                cache.delete(cache_key)
                return user
            else:
                # Increment failed attempts
                cache.set(cache_key, failed_attempts + 1, timeout=3600)
                logger.warning(f"Failed login attempt for: {email}")
                
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            cache.set(cache_key, failed_attempts + 1, timeout=3600)
            logger.warning(f"Failed login attempt for non-existent: {email}")
        
        return None
```

### **13.2 Add to settings.py**
```python
AUTHENTICATION_BACKENDS = [
    'apps.accounts.authentication.CustomAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

## **Step 14: Environment Variables**

**.env.example**
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME=auth_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourapp.com

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Frontend
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# AWS (for production)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Sentry
SENTRY_DSN=

# Admin
DJANGO_SUPERUSER_EMAIL=admin@yourapp.com
DJANGO_SUPERUSER_PASSWORD=admin@123
```

## **Step 15: Running the Application**

### **15.1 Local Development**
```bash
# Clone and setup
git clone <your-repo>
cd auth_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements/development.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your settings

# Start services with Docker
docker-compose up -d db redis

# Run migrations
cd src
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start Celery worker (in another terminal)
celery -A config worker --loglevel=info

# Start Celery beat (in another terminal)
celery -A config beat --loglevel=info
```

### **15.2 Production Deployment**
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Check service status
docker-compose ps
```

## **Step 16: Testing Commands**

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=apps.accounts

# Run specific test
pytest apps/accounts/tests/test_views.py::AuthenticationAPITestCase

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto

# Run security check
bandit -r src/apps

# Run linting
flake8 src
black --check src
isort --check-only src
```

## **Industry Best Practices Implemented**

1. **Security**
   - JWT authentication with refresh token rotation
   - Password strength validation
   - Rate limiting
   - CORS configuration
   - Secure headers
   - SQL injection protection
   - XSS protection
   - CSRF protection
   - Session security

2. **Scalability**
   - Docker containerization
   - Redis caching
   - Celery for async tasks
   - Database connection pooling
   - Nginx load balancing

3. **Reliability**
   - Health checks
   - Monitoring endpoints
   - Error tracking (Sentry)
   - Logging
   - Automated backups

4. **Maintainability**
   - Clean code structure
   - Comprehensive testing
   - API documentation
   - Environment configuration
   - CI/CD pipeline

5. **Performance**
   - Database indexing
   - Query optimization
   - Caching strategy
   - Static file optimization
   - Gunicorn with multiple workers

## **Next Steps for Learning**

1. **Add OAuth2 social authentication** (Google, Facebook, GitHub)
2. **Implement two-factor authentication**
3. **Add API rate limiting with Redis**
4. **Implement API versioning**
5. **Add GraphQL endpoint**
6. **Create admin dashboard with analytics**
7. **Implement webhook system**
8. **Add real-time features with WebSockets**
9. **Implement distributed tracing**
10. **Add performance monitoring with APM tools**

This comprehensive authentication system provides a solid foundation for production applications. It follows industry standards and includes everything needed for a secure, scalable, and maintainable authentication system.