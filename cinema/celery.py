from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем настройки Django для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinema.settings')

app = Celery('cinema')

# Настройки Celery берутся из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
