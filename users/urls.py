from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list", views.participants, name="participants"),
    path("list/", views.participants),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("skills/", views.skill_suggestions, name="skill_suggestions"),
    path("<int:user_id>/skills/add/", views.add_skill, name="add_skill"),
    path(
        "<int:user_id>/skills/<int:skill_id>/remove/",
        views.remove_skill,
        name="remove_skill",
    ),
    path("<int:user_id>/", views.user_detail, name="detail"),
    path("<int:user_id>", views.user_detail),
]
