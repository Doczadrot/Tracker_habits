from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class UserTestCase(APITestCase):
    """Тесты для модели пользователя и аутентификации."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123"
        )

    def test_user_creation(self):
        """Тест создания пользователя."""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpassword123"))
        self.assertIsNotNone(self.user.pk)

    def test_user_str(self):
        """Тест строкового представления пользователя."""
        self.assertEqual(str(self.user), "test@example.com")

    def test_jwt_token_creation(self):
        """Тест создания JWT токена."""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token

        self.assertIsNotNone(access_token)
        self.assertEqual(int(access_token['user_id']), self.user.id)

    def test_user_registration_api(self):
        """Тест регистрации пользователя через API."""
        url = reverse("users:create_user")
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_user_login_api(self):
        """Тест входа пользователя через API."""
        url = reverse("users:user_login")
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_profile_update(self):
        """Тест обновления профиля пользователя."""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-detail")
        data = {
            "tg_chat_id": "123456789"
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.tg_chat_id, "123456789")
