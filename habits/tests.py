from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="user@user.ru")
        self.good_habit = Habit.objects.create(
            user=self.user,
            place="Место 1",
            time="2025-03-30T15:30:00+03:00",
            action="Действие 1",
            is_pleasant=False,
            frequency="m h * * *",
            reward="Вознаграждение 1",
            time_needed=90,
            is_public=True,
        )
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Приятное место 1",
            action="Приятное действие 1",
            is_pleasant=True,
            time_needed=30,
            is_public=False,
            frequency="m h * * *",
        )
        self.user2 = User.objects.create(email="user2@user.ru")
        self.pleasant_habit2 = Habit.objects.create(
            user=self.user2,
            place="Приятное место 2",
            action="Приятное действие 2",
            is_pleasant=True,
            time_needed=30,
            is_public=True,
            frequency="m h * * *",
        )
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Приятное место",
            action="Приятное действие",
            is_pleasant=True,
            time_needed=60,
            is_public=False,
            frequency="m h * * *",
        )

    def test_habit_create(self):
        """Тест на создание привычки."""
        self.client.force_authenticate(user=self.user)
        url = reverse("habits:habit-create")
        data = {
            "place": "Место 1",
            "time": "2025-03-30T15:30:00+03:00",
            "action": "Действие 1",
            "is_pleasant": False,
            "frequency": "m h * * *",
            "reward": "Вознаграждение 1",
            "time_needed": 90,
            "is_public": True,
        }
        request = self.client.post(url, data, format="json")

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_habit_retrieve(self):
        """Тест на получение одной привычки."""
        self.client.force_authenticate(user=self.user)
        url = reverse("habits:habit-detail", args=(self.good_habit.pk,))
        request = self.client.get(url, format="json")
        response = request.json()

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get("action"), self.good_habit.action)

    def test_habit_list(self):
        """Тест на получение списка привычек."""
        self.client.force_authenticate(user=self.user)
        url = reverse("habits:habit-list")
        request = self.client.get(url, format="json")
        response = request.json()

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.get("results")), 3)

    def test_public_habit_list(self):
        """Тест на получение списка публичных привычек."""
        self.client.force_authenticate(user=self.user)
        url = reverse("habits:public-habit-list")
        request = self.client.get(url, format="json")
        response = request.json()

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response,
            [
                {
                    "action": self.good_habit.action,
                    "is_pleasant": self.good_habit.is_pleasant,
                    "time_needed": self.good_habit.time_needed,
                },
                {
                    "action": self.pleasant_habit2.action,
                    "is_pleasant": self.pleasant_habit2.is_pleasant,
                    "time_needed": self.pleasant_habit2.time_needed,
                },
            ],
        )

    def test_habit_update(self):
        """Тест на обновление привычки."""
        url = reverse("habits:habit-update", args=(self.good_habit.pk,))
        body = {
            "place": "Новое приятное место",
            "time": "2025-03-30T15:30:00+03:00",
            "action": "Действие 1",
            "is_pleasant": False,
            "frequency": "m h * * *",
            "reward": "Награда 1",
            "time_needed": 90,
            "is_public": True,
        }
        self.client.force_authenticate(user=self.user)
        request = self.client.patch(url, body, format="json")
        response = request.json()

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get("place"), "Новое приятное место")

    def test_habit_delete(self):
        """Тест на удаление привычки."""
        url = reverse("habits:habit-delete", args=(self.good_habit.pk,))
        self.client.force_authenticate(user=self.user)
        request = self.client.delete(url)
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

    def test_habit_without_auth_is_not_allowed(self):
        """Тест на то, что привычка без авторизации не разрешена."""
        url = reverse("habits:habit-list")
        request = self.client.get(url, format="json")
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)
