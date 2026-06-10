from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "Проверьте email и пароль.",
        "inactive": "Этот аккаунт отключён.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("avatar", "name", "surname", "about", "phone", "github_url")
        labels = {
            "avatar": "Аватар",
            "name": "Имя",
            "surname": "Фамилия",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 5}),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/username"}
            ),
        }


class TeamFinderPasswordChangeForm(PasswordChangeForm):
    pass
