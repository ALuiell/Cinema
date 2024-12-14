#!/bin/bash
VENV_DIR="/home/aluiel3/.virtualenvs/myvirtualenv"
#!/bin/bash

PROJECT_DIR="/home/aluiel3/cinema"
LOG_FILE="/home/aluiel3/cinema/git_pull.log"
VENV_DIR="/home/aluiel3/.virtualenvs/myvirtualenv"

cd $PROJECT_DIR || { echo "[$(date)] Ошибка: не удалось перейти в директорию $PROJECT_DIR" >> $LOG_FILE; exit 1; }

# Активация виртуального окружения
source /home/aluiel3/.virtualenvs/myvirtualenv/bin/activate || { echo "[$(date)] Ошибка: не удалось активировать виртуальное окружение" >> $LOG_FILE; exit 1; }

if git pull origin master --force >> $LOG_FILE 2>&1; then
    echo "[$(date)] Успешное обновление из репозитория." >> $LOG_FILE
else
    echo "[$(date)] Ошибка: не удалось выполнить git pull." >> $LOG_FILE
fi

# Сбор статических файлов
if python manage.py collectstatic --noinput >> $LOG_FILE 2>&1; then
    echo "[$(date)] Статические файлы собраны." >> $LOG_FILE
else
    echo "[$(date)] Ошибка при сборе статических файлов." >> $LOG_FILE
fi

# Деактивация виртуального окружения
deactivate
