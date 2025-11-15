# Import celery app if available
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed, create a dummy app
    celery_app = None
    __all__ = ()
