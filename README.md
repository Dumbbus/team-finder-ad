# TeamFinder

TeamFinder - это веб-приложение для поиска людей в команду pet-проекта. Идея простая: пользователь публикует проект, описывает, что хочет сделать, а другие участники могут посмотреть идею, добавить её в избранное или присоединиться к команде.

Проект сделан как учебное Django-приложение с готовым HTML/CSS/JS-фронтендом и полноценным backend-слоем: моделями, формами, авторизацией, PostgreSQL, демоданными и базовыми автотестами.

## Возможности

- регистрация и вход пользователей по email;
- публичные профили участников;
- редактирование профиля, телефона, GitHub-ссылки и аватара;
- автоматическая генерация аватара с первой буквой имени;
- создание и редактирование проектов;
- список всех проектов с пагинацией;
- детальная страница проекта;
- добавление проектов в избранное;
- участие и отказ от участия в чужих проектах;
- завершение проекта автором;
- список избранных проектов;
- список участников с фильтрами по активности;
- команда для заполнения базы демонстрационными данными.

## Стек

- Python 3.12+
- Django 5.2
- PostgreSQL 16
- Docker Compose
- psycopg 3
- Pillow
- python-decouple
- HTML, CSS, JavaScript

## Как запустить проект

### 1. Склонировать репозиторий

```bash
git clone <ссылка-на-репозиторий>
cd team-finder-ad
```

### 2. Создать виртуальное окружение

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Подготовить переменные окружения

Создайте файл `.env` на основе `.env_example`:

```bash
cp .env_example .env
```

На Windows можно просто создать копию файла `.env_example` и назвать её `.env`.

Пример содержимого:

```env
DJANGO_SECRET_KEY=change_for_safety
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,testserver

POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

TASK_VERSION=1
```

### 5. Запустить PostgreSQL

Убедитесь, что Docker Desktop запущен, затем выполните:

```bash
docker compose up -d
```

Если база уже создавалась раньше с другими логином или паролем, можно пересоздать volume:

```bash
docker compose down -v
docker compose up -d
```

Команда `down -v` удаляет данные PostgreSQL из контейнера, поэтому используйте её только если локальные данные не нужны.

### 6. Выполнить миграции

```bash
python manage.py migrate
```

### 7. Заполнить базу демоданными

```bash
python manage.py seed_demo_data
```

Демо-пользователи:

| Email | Пароль |
| --- | --- |
| `anna@example.com` | `demo12345` |
| `ivan@example.com` | `demo12345` |
| `maria@example.com` | `demo12345` |

### 8. Запустить сервер

```bash
python manage.py runserver
```

После запуска приложение будет доступно по адресу:

[http://127.0.0.1:8000/projects/list](http://127.0.0.1:8000/projects/list)


## Автор

Проект подготовил Lunishko.

Связаться со мной можно по почте: [morakovkarssar@gmail.com](mailto:morakovkarssar@gmail.com).
