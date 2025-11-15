import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brandtracker.settings')

try:
    from celery import Celery
    app = Celery('brandtracker')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
except ImportError:
    # Celery not installed, create a dummy app
    app = None
