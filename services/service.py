import json
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from constants import *

CYRILLIC_MAP = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
}


def pagination_query_prefix(request):
    params = request.GET.copy()
    params.pop("page", None)
    encoded = urlencode(params, doseq=True)
    return f"{encoded}&" if encoded else ""


def json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def pagination(request, contents, per_page):
    paginator = Paginator(contents, per_page)
    return paginator.get_page(request.GET.get("page"))


@require_GET
def skill_suggestions(request):
    from users.models import Skill
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()
    if query:
        skills = skills.filter(name__icontains=query)
    data = [{"id": skill.id, "name": skill.name} for skill in skills[:SKILL_TRUNCATION_TAIL]]
    return JsonResponse(data, safe=False)

def transliterate(text):
    return ''.join(CYRILLIC_MAP.get(ch, ch) for ch in text)

def default_avatar_name(user):
    email_part = user.email.split("@", 1)[0] if user.email else "user"
    return f"avatars/default_{email_part}.png"

def make_initial_avatar(user):
    raw_name = user.name or user.email or "user"
    safe_name = transliterate(raw_name)
    letter = (safe_name or user.email or "U").strip()[:1].upper() or "U"
    palette = list(Colors)
    color = palette[sum(ord(ch) for ch in letter) % (len(palette) - 1)]

    image = Image.new("RGB", IMAGE_SIZE, color)
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size=IMAGE_FONT_SIZE)
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (IMAGE_SIZE[0] - (bbox[2] - bbox[0])) / 2
    y = (IMAGE_SIZE[1] - (bbox[3] - bbox[1])) / 2 - 8
    draw.text((x, y), letter, fill=Colors.CLASSIC_ANTHRACITE, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=Path(default_avatar_name(user)).name)

