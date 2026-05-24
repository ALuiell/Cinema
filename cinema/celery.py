from __future__ import absolute_import, unicode_literals
import os

try:
    from celery import Celery
except ImportError:  # pragma: no cover - optional dependency for local study setup
    Celery = None


os.environ['DJANGO_SETTINGS_MODULE'] = 'cinema.settings'

if Celery is not None:
    app = Celery('cinema')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
else:
    app = None

    def debug_task(*args, **kwargs):
        raise RuntimeError('Celery is not installed in this local setup.')


if app is not None:
    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
