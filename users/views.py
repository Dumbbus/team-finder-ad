import json
from urllib.parse import urlencode

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import (
    EmailAuthenticationForm,
    ProfileForm,
    RegisterForm,
    TeamFinderPasswordChangeForm,
)
from .models import Skill, User


def _pagination_query_prefix(request):
    params = request.GET.copy()
    params.pop("page", None)
    encoded = urlencode(params, doseq=True)
    return f"{encoded}&" if encoded else ""


def _json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
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
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.id)

    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password(request):
    form = TeamFinderPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
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

    paginator = Paginator(users, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/participants.html",
        {
            "page_obj": page_obj,
            "participants": users,
            "active_filter": active_filter,
            "active_skill": active_filter,
            "skills": Skill.objects.all(),
            "query_prefix": _pagination_query_prefix(request),
        },
    )


@require_GET
def skill_suggestions(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()
    if query:
        skills = skills.filter(name__icontains=query)
    data = [{"id": skill.id, "name": skill.name} for skill in skills[:10]]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill(request, user_id):
    if request.user.id != user_id:
        return HttpResponseForbidden("Можно редактировать только свой профиль")

    payload = _json_body(request)
    skill = None
    if payload.get("skill_id"):
        skill = get_object_or_404(Skill, pk=payload["skill_id"])
    elif payload.get("name"):
        skill_name = payload["name"].strip()
        if skill_name:
            skill, _ = Skill.objects.get_or_create(name=skill_name)

    if skill is None:
        return JsonResponse({"error": "skill is required"}, status=400)

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
