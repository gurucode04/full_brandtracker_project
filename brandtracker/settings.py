import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET', 'dev-secret')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'corsheaders',
    'tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Allow all origins in development (for easier testing)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

ROOT_URLCONF = 'brandtracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'tracker' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': ['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']},
    }
]

WSGI_APPLICATION = 'brandtracker.wsgi.application'
ASGI_APPLICATION = 'brandtracker.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Channel layers configuration with fallback
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Try to use Redis if available
try:
    import redis
    from redis.exceptions import ConnectionError as RedisConnectionError
    
    try:
        redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
        redis_client = redis.Redis(host=redis_host, port=6379, db=0, socket_connect_timeout=2)
        redis_client.ping()
        # Redis is available, use it
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': { 'hosts': [(redis_host, 6379)] },
            }
        }
    except (RedisConnectionError, redis.ConnectionError, Exception) as e:
        # Redis not available, use in-memory (already set above)
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Redis not available, using in-memory channel layer: {e}")
except ImportError:
    # redis package not installed
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Redis package not installed, using in-memory channel layer")

# Celery configuration with fallback
# Default to Redis, but will fall back gracefully if not available
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Try to verify Redis connection for Celery
try:
    import redis
    from redis.exceptions import ConnectionError as RedisConnectionError
    try:
        redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
        test_client = redis.Redis(host=redis_host, port=6379, db=0, socket_connect_timeout=2)
        test_client.ping()
        # Redis is available, use it for Celery
        CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', f'redis://{redis_host}:6379/0')
        CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    except (RedisConnectionError, redis.ConnectionError, Exception) as e:
        # Redis not available - Celery tasks won't work, but app will still run
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Redis not available for Celery. Celery tasks will not work. Error: {e}")
        logger.warning("To enable Celery, please start Redis: redis-server")
        # Keep the Redis URL - Celery will fail gracefully when trying to connect
        # This allows the app to start even without Redis
except ImportError:
    # redis package not installed
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Redis package not installed. Celery tasks will not work.")

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'tracker' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
