"""
Простые health check views для новичков
"""
from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Простой health check - проверяет только базовую работоспособность
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Habits API работает!'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
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