from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .validators import validate_github_url
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
        "invalid_login": "Неверный имейл или пароль.",
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
        widgets = {
            "about": forms.Textarea(attrs={"rows": 5}),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/username"}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            raise forms.ValidationError("Укажите номер телефона.")

        if phone.startswith("8") and len(phone) == 11 and phone.isdigit():
            phone = "+7" + phone[1:]
        elif phone.startswith("+7") and len(phone) == 12 and phone[2:].isdigit():
            pass
        else:
            raise forms.ValidationError("Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")

        legacy_phone = "8" + phone[2:]
        duplicates = User.objects.filter(phone__in=[phone, legacy_phone])
        if self.instance and self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует.")
        return phone

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", ""))


class TeamFinderPasswordChangeForm(PasswordChangeForm):
    pass
