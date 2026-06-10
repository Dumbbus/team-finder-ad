from django.conf import settings
from django.db import models

from users.models import Skill


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = (
        (STATUS_OPEN, "Открыт"),
        (STATUS_CLOSED, "Закрыт"),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    name = models.CharField("Название", max_length=160)
    description = models.TextField("Описание")
    github_url = models.URLField("GitHub", blank=True)
    status = models.CharField(
        "Статус",
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participating_projects",
        blank=True,
        verbose_name="Участники",
    )
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="favorites",
        blank=True,
        verbose_name="В избранном у",
    )
    required_skills = models.ManyToManyField(
        Skill,
        related_name="projects",
        blank=True,
        verbose_name="Необходимые навыки",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name
