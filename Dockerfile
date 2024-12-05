# Используем Python 3.12 как базовый образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем весь проект
COPY . /app

# Указываем, что можно передавать команду через docker-compose
ENTRYPOINT ["sh", "-c"]
CMD ["python manage.py runserver 0.0.0.0:8000"]
