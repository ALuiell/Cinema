
FROM python:3.12-slim

WORKDIR /app


COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . /app

ENTRYPOINT ["sh", "-c"]
CMD ["python manage.py runserver 0.0.0.0:8000"]
