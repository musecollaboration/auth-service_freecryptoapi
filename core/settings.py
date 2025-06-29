"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""


from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / 'core' / '.env')


# Настройки логирования

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',

    'apps.common.apps.CommonConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.crypto.apps.CryptoConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Настройка аутентификации и авторизации
AUTH_USER_MODEL = 'accounts.User'


# Настройка SHELL_PLUS для Django Extensions
SHELL_PLUS = "ipython"  # Использует IPython при запуске `python manage.py shell`


# Основные настройки DRF
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",  # Генерация OpenAPI схемы через drf-spectacular

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',   # JWT-аутентификация
    ],
}

# Настройки API-документации DRF Spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Crypto API",  # Название API проекта
    "VERSION": "0.0.1",  # Версия API
    "SERVE_INCLUDE_SCHEMA": False,  # Исключает эндпоинт `/schema` из публичного API,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,  # не сбрасывать авторизацию при перезагрузке страницы
    },
}

# Настройки JWT
SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

# Настройки кэша
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',                     # 1 - основной кэш
    },
    'cache-for-ratelimiting': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/2',                     # 2 - кэш для ratelimit
    },
    'crypto': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/3',                     # 3 - кэш для криптовалют
    },
}


# Настройки ratelimit
RATELIMIT_USE_CACHE = 'cache-for-ratelimiting'  # Привязываем ratelimit к отдельному кэшу


# Настройки электронной почты
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Конфигурация сервера электронной почты
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'cahdro2155@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
DEBUG
SITE_URL = 'http://localhost:8000'  # Измените на реальный URL вашего сайта, при деплое


# Настройки Celery
CELERY_BROKER_URL = 'redis://localhost:6379/3'      # 3 - очередь для задач
CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'  # 3 - кэш для результатов выполнения задач

# Временная зона для задач
CELERY_TIMEZONE = "UTC"

# Включаем отслеживание выполнения задач
CELERY_TASK_TRACK_STARTED = True           # Отслеживание начала выполнения задач
CELERY_TASK_ALWAYS_EAGER = False           # Если False, задачи отправляются в очередь и обрабатываются воркером.
CELERY_TASK_RESULT_EXPIRES = 3600          # Время жизни результатов задач в секундах


# Настройки Coingecko API
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")


# Настройки RabbitMQ
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"  # URL подключения к RabbitMQ


# Настройки режима разработки для приложения crypto
API_ALLOW_FALLBACK = True if DEBUG else False # на продакшене нужно устанавливать False
