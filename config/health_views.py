"""
Простые health check views для новичков
"""
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """
    Простой health check - проверяет только базовую работоспособность
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Habits API работает!'
    })


def detailed_health_check(request):
    """
    Более детальный health check - проверяет подключение к БД
    """
    try:
        # Простая проверка БД
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return JsonResponse({
        'status': 'ok' if db_status == 'ok' else 'error',
        'database': db_status,
        'message': 'Детальная проверка здоровья API'
    })
