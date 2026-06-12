from urllib.parse import urlparse

from django import forms


def validate_github_url(value):
    if not value:
        return value
    host = urlparse(value).netloc.lower()
    if host not in {"github.com", "www.github.com"}:
        raise forms.ValidationError("Ссылка должна вести на GitHub.")
    return value
