from django.test import TestCase
from django.urls import reverse

from .models import User


class UserFlowTests(TestCase):
    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Анна",
                "surname": "Смирнова",
                "email": "anna@example.com",
                "password": "demo12345",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="anna@example.com").exists())

    def test_login_uses_email_and_password(self):
        User.objects.create_user(
            email="ivan@example.com",
            password="demo12345",
            name="Иван",
            surname="Петров",
        )

        response = self.client.post(
            reverse("users:login"),
            {"email": "ivan@example.com", "password": "demo12345"},
        )

        self.assertRedirects(response, reverse("projects:list"))

    def test_participants_page_is_public(self):
        response = self.client.get(reverse("users:participants"))

        self.assertEqual(response.status_code, 200)
