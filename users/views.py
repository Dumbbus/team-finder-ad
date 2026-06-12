from http import HTTPStatus

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from constants import USERS_PER_PAGE
from services.service import pagination_query_prefix, json_body, pagination, skill_suggestions
from .forms import (
    EmailAuthenticationForm,
    ProfileForm,
    RegisterForm,
    TeamFinderPasswordChangeForm,
)
from .models import Skill, User


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = EmailAuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "projects:list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects__participants"),
        pk=user_id,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.id)

    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password(request):
    form = TeamFinderPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", user_id=request.user.id)

    return render(request, "users/change_password.html", {"form": form})


def participants(request):
    users = User.objects.order_by("id")
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        current_user = request.user
        if active_filter == "owners-of-favorite-projects":
            users = users.filter(owned_projects__interested_users=current_user)
        elif active_filter == "owners-of-participating-projects":
            users = users.filter(owned_projects__participants=current_user)
        elif active_filter == "interested-in-my-projects":
            users = users.filter(favorites__owner=current_user)
        elif active_filter == "participants-of-my-projects":
            users = users.filter(participated_projects__owner=current_user)

        users = users.exclude(pk=current_user.pk).distinct()

    page_obj = pagination(request, users, USERS_PER_PAGE)
    return render(
        request,
        "users/participants.html",
        {
            "page_obj": page_obj,
            "participants": users,
            "active_filter": active_filter,
            "active_skill": active_filter,
            "skills": Skill.objects.all(),
            "query_prefix": pagination_query_prefix(request),
        },
    )


@login_required
@require_POST
def add_skill(request, user_id):
    if request.user.id != user_id:
        return HttpResponseForbidden("Можно редактировать только свой профиль")

    payload = json_body(request)
    skill = None
    if payload.get("skill_id"):
        skill = get_object_or_404(Skill, pk=payload["skill_id"])
    elif payload.get("name"):
        skill_name = payload["name"].strip()
        if skill_name:
            skill, _ = Skill.objects.get_or_create(name=skill_name)

    if skill is None:
        return JsonResponse({"error": "skill is required"}, status=HTTPStatus.BAD_REQUEST)

    request.user.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@login_required
@require_POST
def remove_skill(request, user_id, skill_id):
    if request.user.id != user_id:
        return HttpResponseForbidden("Можно редактировать только свой профиль")
    skill = get_object_or_404(Skill, pk=skill_id)
    request.user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
