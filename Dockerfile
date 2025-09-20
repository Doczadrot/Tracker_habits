# Multi-stage build для оптимизации размера образа

# Stage 1: Build stage
FROM python:3.12-slim as builder

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt ./

# Создаем виртуальное окружение и устанавливаем зависимости
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-slim

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копируем виртуальное окружение из builder stage
COPY --from=builder /opt/venv /opt/venv

# Устанавливаем PATH для использования venv
ENV PATH="/opt/venv/bin:$PATH"

# Создаем пользователя для безопасности
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код приложения
COPY --chown=appuser:appuser . .

# Создаем необходимые директории
RUN mkdir -p /app/static /app/media /app/logs && \
    chown -R appuser:appuser /app

# Делаем entrypoint скрипт исполняемым
RUN chmod +x docker-entrypoint.sh

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт
EXPOSE 8000

# Добавляем health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Устанавливаем entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Команда по умолчанию
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "30", "--keep-alive", "2", "config.wsgi:application"]
