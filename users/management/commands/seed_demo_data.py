from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


class Command(BaseCommand):
    help = "Create demo users and projects for TeamFinder."

    def handle(self, *args, **options):
        skills = {}
        for name in ["Django", "PostgreSQL", "React", "UX", "Docker", "Python"]:
            skills[name], _ = Skill.objects.get_or_create(name=name)

        users_data = [
            {
                "email": "anna@example.com",
                "name": "Анна",
                "surname": "Смирнова",
                "about": "Backend-разработчик, люблю аккуратные API и понятные процессы.",
                "phone": "+7 900 111-22-33",
                "github_url": "https://github.com/anna-teamfinder",
                "skills": ["Django", "PostgreSQL", "Python"],
                "project": {
                    "name": "PetCollab",
                    "description": "Сервис для поиска напарников по небольшим pet-проектам.",
                    "github_url": "https://github.com/example/petcollab",
                },
            },
            {
                "email": "ivan@example.com",
                "name": "Иван",
                "surname": "Петров",
                "about": "Frontend-разработчик, собираю быстрые интерфейсы для команд.",
                "phone": "+7 900 222-33-44",
                "github_url": "https://github.com/ivan-teamfinder",
                "skills": ["React", "UX"],
                "project": {
                    "name": "DesignSprint Board",
                    "description": "Доска для подготовки и проведения продуктовых дизайн-спринтов.",
                    "github_url": "https://github.com/example/designsprint-board",
                },
            },
            {
                "email": "maria@example.com",
                "name": "Мария",
                "surname": "Кузнецова",
                "about": "DevOps-инженер, помогаю проектам удобно запускаться и деплоиться.",
                "phone": "+7 900 333-44-55",
                "github_url": "https://github.com/maria-teamfinder",
                "skills": ["Docker", "PostgreSQL"],
                "project": {
                    "name": "Deploy Notes",
                    "description": "Приложение для хранения чек-листов деплоя и командных заметок.",
                    "github_url": "https://github.com/example/deploy-notes",
                },
            },
        ]

        created_users = []
        for user_data in users_data:
            project_data = user_data.pop("project")
            user_skills = user_data.pop("skills")
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults=user_data,
            )
            if created:
                user.set_password("demo12345")
                user.save(update_fields=["password"])
            else:
                for field, value in user_data.items():
                    setattr(user, field, value)
                user.set_password("demo12345")
                user.save()

            user.skills.set([skills[name] for name in user_skills])
            created_users.append(user)

            project, _ = Project.objects.get_or_create(
                owner=user,
                name=project_data["name"],
                defaults={
                    "description": project_data["description"],
                    "github_url": project_data["github_url"],
                },
            )
            project.participants.add(user)
            project.required_skills.set(user.skills.all())

        if len(created_users) >= 3:
            first, second, third = created_users
            first.favorites.add(second.owned_projects.first())
            second.favorites.add(third.owned_projects.first())
            third.favorites.add(first.owned_projects.first())
            first.participated_projects.add(third.owned_projects.first())
            second.participated_projects.add(first.owned_projects.first())

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data is ready. Users: anna@example.com, "
                "ivan@example.com, maria@example.com. Password: demo12345."
            )
        )
