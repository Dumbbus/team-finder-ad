from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Skill, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("email", "name", "surname", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("email", "name", "surname")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {
                "fields": (
                    "name",
                    "surname",
                    "about",
                    "phone",
                    "github_url",
                    "avatar",
                    "skills",
                )
            },
        ),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions", "skills")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)
