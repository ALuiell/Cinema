import os
import django
from django.db import connections
from django.db.utils import OperationalError

# Настройте переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinema.settings')
django.setup()

db_conn = connections['default']
try:
    db_conn.cursor()
    print("Подключение к базе данных успешно")
except OperationalError as e:
    print(f"Не удалось подключиться к базе данных: {e}")
