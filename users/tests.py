from django.test import TestCase
from django.urls import reverse

from .models import User


class UserFlowTests(TestCase):
    def test_register_creates_user_logs_in_and_redirects_to_projects(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Анна",
                "surname": "Смирнова",
                "email": "anna@example.com",
                "password": "demo12345",
            },
        )

        self.assertRedirects(response, reverse("projects:list"))
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

    def test_profile_form_normalizes_and_validates_unique_phone(self):
        first = User.objects.create_user(
            email="first@example.com",
            password="demo12345",
            name="Первый",
            surname="Пользователь",
            phone="+79001112233",
        )
        second = User.objects.create_user(
            email="second@example.com",
            password="demo12345",
            name="Второй",
            surname="Пользователь",
        )
        self.client.force_login(second)

        response = self.client.post(
            reverse("users:edit_profile"),
            {
                "name": second.name,
                "surname": second.surname,
                "about": "",
                "phone": "89001112233",
                "github_url": "https://github.com/second",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользователь с таким телефоном уже существует.")
        self.assertEqual(first.phone, "+79001112233")

    def test_profile_rejects_non_github_url(self):
        user = User.objects.create_user(
            email="profile@example.com",
            password="demo12345",
            name="Профиль",
            surname="Тестовый",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:edit_profile"),
            {
                "name": user.name,
                "surname": user.surname,
                "about": "",
                "phone": "+79004445566",
                "github_url": "https://gitlab.com/profile",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ссылка должна вести на GitHub.")
