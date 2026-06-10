from django.test import TestCase
from django.urls import reverse

from users.models import User

from .models import Project


class ProjectFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="demo12345",
            name="Ольга",
            surname="Авторова",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="demo12345",
            name="Максим",
            surname="Участников",
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name="TeamFinder",
            description="Поиск команды для pet-проектов.",
        )
        self.project.participants.add(self.owner)

    def test_project_list_is_public(self):
        response = self.client.get(reverse("projects:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TeamFinder")

    def test_authenticated_user_can_create_project(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "New Project",
                "description": "Новый проект для проверки.",
                "github_url": "",
                "status": Project.STATUS_OPEN,
            },
        )

        project = Project.objects.get(name="New Project")
        self.assertRedirects(response, reverse("projects:detail", args=[project.id]))
        self.assertEqual(project.owner, self.member)
        self.assertIn(self.member, project.participants.all())

    def test_toggle_favorite_adds_and_removes_project(self):
        self.client.force_login(self.member)

        add_response = self.client.post(reverse("projects:toggle_favorite", args=[self.project.id]))
        remove_response = self.client.post(reverse("projects:toggle_favorite", args=[self.project.id]))

        self.assertJSONEqual(add_response.content, {"status": "ok", "favorite": True})
        self.assertJSONEqual(remove_response.content, {"status": "ok", "favorite": False})
        self.assertFalse(self.member.favorites.filter(pk=self.project.pk).exists())

    def test_toggle_participate_adds_member(self):
        self.client.force_login(self.member)

        response = self.client.post(reverse("projects:toggle_participate", args=[self.project.id]))

        self.assertJSONEqual(response.content, {"status": "ok", "participant": True})
        self.assertIn(self.member, self.project.participants.all())

    def test_owner_can_complete_project(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("projects:complete", args=[self.project.id]))
        self.project.refresh_from_db()

        self.assertJSONEqual(response.content, {"status": "ok"})
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)
