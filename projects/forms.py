from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 7}),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/team/project"}
            ),
        }
