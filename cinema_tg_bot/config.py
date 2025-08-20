import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema.settings_prod")
django.setup()

from django.conf import settings

BOT_NAME = settings.TELEGRAM_BOT_NAME
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
API_BASE_URL = settings.API_BASE_URL
EMAIL_PATTERN = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
CODE_PATTERN = r"^\d{6,10}$"