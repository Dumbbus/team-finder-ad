import django.conf
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Название")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("github_url", models.URLField(blank=True, verbose_name="GitHub")),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("closed", "Closed")],
                        default="open",
                        max_length=6,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Дата создания"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_projects",
                        to=django.conf.settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "participants",
                    models.ManyToManyField(
                        blank=True,
                        related_name="participated_projects",
                        to=django.conf.settings.AUTH_USER_MODEL,
                        verbose_name="Участники",
                    ),
                ),
                (
                    "required_skills",
                    models.ManyToManyField(
                        blank=True,
                        related_name="projects",
                        to="users.skill",
                        verbose_name="Необходимые навыки",
                    ),
                ),
            ],
            options={
                "verbose_name": "Проект",
                "verbose_name_plural": "Проекты",
                "ordering": ("-created_at",),
            },
        ),
    ]
