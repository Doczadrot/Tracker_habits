from unittest.mock import Mock, patch

import pytest
from django.test import TestCase

from habits.models import Habit
from habits.task import send_message
from users.models import User


class CeleryTasksTestCase(TestCase):
    """Тесты для Celery задач."""

    def setUp(self):
        self.user = User.objects.create(
            email="test@test.com",
            tg_chat_id="123456789"
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place="Тестовое место",
            action="Тестовое действие",
            reward="Тестовое вознаграждение",
            time_needed=60,
            is_pleasant=False,
            is_public=True,
            frequency="m h * * *",
        )

    @patch('habits.task.requests.get')
    def test_send_message_with_reward(self, mock_get):
        """Тест отправки сообщения с вознаграждением."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Выполняем задачу
        send_message(self.habit.pk)

        # Проверяем, что requests.get был вызван
        mock_get.assert_called_once()

        # Проверяем параметры вызова
        call_args = mock_get.call_args
        self.assertIn('sendMessage', call_args[0][0])

        params = call_args[1]['params']
        self.assertEqual(params['chat_id'], self.user.tg_chat_id)
        self.assertIn(self.habit.action, params['text'])
        self.assertIn(self.habit.place, params['text'])
        self.assertIn(self.habit.reward, params['text'])

    @patch('habits.task.requests.get')
    def test_send_message_with_related_habit(self, mock_get):
        """Тест отправки сообщения со связанной привычкой."""
        # Создаем связанную приятную привычку
        related_habit = Habit.objects.create(
            user=self.user,
            place="Приятное место",
            action="Приятное действие",
            is_pleasant=True,
            time_needed=30,
            is_public=True,
            frequency="m h * * *",
        )

        # Обновляем основную привычку
        self.habit.related_habit = related_habit
        self.habit.reward = None
        self.habit.save()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Выполняем задачу
        send_message(self.habit.pk)

        # Проверяем, что requests.get был вызван
        mock_get.assert_called_once()

        # Проверяем параметры вызова
        call_args = mock_get.call_args
        params = call_args[1]['params']
        self.assertIn(related_habit.action, params['text'])

    def test_send_message_nonexistent_habit(self):
        """Тест отправки сообщения для несуществующей привычки."""
        with pytest.raises(Habit.DoesNotExist):
            send_message(99999)

    @patch('habits.task.requests.get')
    def test_send_message_user_without_tg_chat_id(self, mock_get):
        """Тест отправки сообщения пользователю без Telegram ID."""
        # Создаем пользователя без tg_chat_id
        user_no_tg = User.objects.create(email="notg@test.com")
        habit_no_tg = Habit.objects.create(
            user=user_no_tg,
            place="Место",
            action="Действие",
            reward="Вознаграждение",
            time_needed=30,
            is_pleasant=False,
            is_public=True,
            frequency="m h * * *",
        )

        # Выполняем задачу - не должно падать
        send_message(habit_no_tg.pk)

        # requests.get не должен вызываться для пользователя без tg_chat_id
        mock_get.assert_not_called()
