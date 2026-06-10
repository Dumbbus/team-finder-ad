import json
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from users.models import Skill

from .forms import ProjectForm
from .models import Project


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


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related(
        "participants",
        "favorited_by",
    )
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
            "page_obj": page_obj,
            "query_prefix": _pagination_query_prefix(request),
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants",
            "favorited_by",
        ),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner").prefetch_related(
        "participants",
        "favorited_by",
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
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
    if request.method == "POST" and form.is_valid():
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
        return JsonResponse({"status": "forbidden"}, status=403)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status", "updated_at"])
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorite = False
    else:
        request.user.favorites.add(project)
        favorite = True
    return JsonResponse({"status": "ok", "favorite": favorite})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "forbidden"}, status=403)
    if project.status == Project.STATUS_CLOSED:
        return JsonResponse({"status": "closed"}, status=400)

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse({"status": "ok", "participant": participant})


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
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Редактировать навыки проекта может только автор")

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
