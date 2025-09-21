import requests
from celery import shared_task

from config.settings import TELEGRAM_BOT_TOKEN
from habits.models import Habit


@shared_task
def send_message(pk) -> None:
    """Отправляет напоминания в телеграм пользователя."""
    habit = Habit.objects.get(pk=pk)

    # Проверяем, есть ли у пользователя tg_chat_id
    if not habit.user.tg_chat_id:
        return

    reward_text = habit.reward if habit.reward else (habit.related_habit.action if habit.related_habit else '')
    text = (
        f"Пришло время сделать '{habit.action}' в '{habit.place}'! "
        f"Не забудьте '{reward_text}' после."
    )
    params = {
        'text': text,
        'chat_id': habit.user.tg_chat_id,
    }
    requests.get(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', params=params)
