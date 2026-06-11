from io import BytesIO
from pathlib import Path

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField("Название", max_length=80, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


def _default_avatar_name(user):
    email_part = user.email.split("@", 1)[0] if user.email else "user"
    return f"avatars/default_{email_part}.png"


def _make_initial_avatar(user):
    letter = (user.name or user.email or "U").strip()[:1].upper() or "U"
    palette = ["#DDE7F2", "#E5E7D6", "#F1E2D2", "#DEE8DD", "#E8DEEA"]
    color = palette[sum(ord(ch) for ch in letter) % len(palette)]

    image = Image.new("RGB", (256, 256), color)
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size=120)
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (256 - (bbox[2] - bbox[0])) / 2
    y = (256 - (bbox[3] - bbox[1])) / 2 - 8
    draw.text((x, y), letter, fill="#2F3437", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=Path(_default_avatar_name(user)).name)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    about = models.TextField("О себе", max_length=256, blank=True)
    phone = models.CharField("Телефон", max_length=12, blank=True)
    github_url = models.URLField("GitHub", blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    skills = models.ManyToManyField(Skill, related_name="users", blank=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Доступ в админку", default=False)
    date_joined = models.DateTimeField("Дата регистрации", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ("-date_joined",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{self.name} {self.surname}".strip()

    def get_short_name(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(_default_avatar_name(self), _make_initial_avatar(self), save=True)
        super().save(*args, **kwargs)
