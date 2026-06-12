from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from constants import *
from services.service import pagination_query_prefix, json_body, pagination, skill_suggestions
from users.models import Skill
from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related(
        "participants",
        "interested_users",
    )
    page_obj = pagination(request, projects, PROJECTS_PER_PAGE)
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
            "page_obj": page_obj,
            "query_prefix": pagination_query_prefix(request),
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants",
            "interested_users",
        ),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner").prefetch_related(
        "participants",
        "interested_users",
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.id)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Редактировать проект может только автор")

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "forbidden"}, status=HTTPStatus.FORBIDDEN)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "closed", "project_status": project.status},
                            status=HTTPStatus.BAD_REQUEST, )

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status", "updated_at"])
    return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if fav_filter := request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not fav_filter})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "forbidden"}, status=HTTPStatus.FORBIDDEN)
    if project.status == Project.STATUS_CLOSED:
        return JsonResponse({"status": "closed"}, status=HTTPStatus.BAD_REQUEST)
    if part_filter := project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": not part_filter})
    project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not part_filter})


@login_required
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Редактировать навыки проекта может только автор")

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

    project.required_skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@login_required
@require_POST
def remove_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Редактировать навыки проекта может только автор")
    skill = get_object_or_404(Skill, pk=skill_id)
    project.required_skills.remove(skill)
    return JsonResponse({"status": "ok"})
