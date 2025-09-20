#!/bin/bash

# Ждем доступности базы данных
echo "Waiting for postgres..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Ждем доступности Redis
echo "Waiting for redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

# Создаем директорию для логов
mkdir -p /app/logs

# Выполняем миграции
echo "Running migrations..."
python manage.py migrate

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "Starting server..."
exec "$@"
