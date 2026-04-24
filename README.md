# Blogicum — Sprint 4

Extended Django blog platform built on top of [Sprint 3](https://github.com/Shipovmax/django_sprint3) — adds user registration, profiles, comments, image upload, pagination, and password management. Comes with a comprehensive pytest suite covering all new features.

---

## New features vs Sprint 3

- **User auth** — registration, login, logout via `django.contrib.auth.urls`
- **User profile** — public profile page; editable personal info
- **Password management** — change, reset, reset confirmation via email
- **Comments** — CRUD on posts; FK to `Post` and `User`; author-only edit/delete; `created_at` auto timestamp
- **Post image upload** — `Post.image` (`ImageField`), Pillow for processing
- **Post CRUD for authors** — create, edit, delete own posts; 403/redirect for non-authors
- **Pagination** — 10 posts per page on index, category, and profile pages
- **Error pages** — custom 403csrf, 404, 500 templates
- **Bootstrap 5** — via `django-bootstrap5`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3 |
| Framework | Django 3.2 |
| Frontend | Bootstrap 5 (`django-bootstrap5`) |
| Images | Pillow 9.3 |
| Testing | pytest, pytest-django, mixer, Faker, BeautifulSoup4 |
| Linting | flake8, flake8-docstrings, pep8-naming |

---

## Quick Start

```bash
git clone https://github.com/Shipovmax/django_sprint4
cd django_sprint4

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cd blogicum
python manage.py migrate
python manage.py loaddata ../db.json
python manage.py runserver
```

---

## Running Tests

```bash
pytest
```

| Test file | Coverage |
|-----------|---------|
| `test_post.py` | Post model attrs, image field, create/edit/delete, scheduled posts |
| `test_comment.py` | Comment model attrs, CRUD, author permissions |
| `test_content.py` | Feed content, pagination, post ordering |
| `test_edit.py` | Edit/delete access control (author vs other user) |
| `test_users.py` | Registration, profile view, profile edit, auth URLs |
| `test_emails.py` | Password reset email flow |
| `test_err_pages.py` | Custom 404/500/403csrf handler registration |
| `test_static_pages.py` | About and Rules pages |

Test infrastructure includes adapters, fixtures, and form testers for posts, comments, and users — all in `tests/`.

---

## Project Structure

```
django_sprint4/
├── blogicum/           # Django project (blog, pages, core apps)
├── templates/
│   ├── blog/           # index, detail, category, profile, comment, create
│   ├── registration/   # login, signup, password change/reset templates
│   └── pages/          # about, rules, 403csrf, 404, 500
├── tests/
│   ├── adapters/       # Model adapters for post, comment, user
│   ├── fixtures/       # pytest fixtures for posts, comments, locations
│   ├── form/           # Form testers for post, comment, user CRUD
│   └── test_*.py       # 8 test files
├── db.json
└── requirements.txt
```

---

## Author

- GitHub: [Shipovmax](https://github.com/Shipovmax)
- Email: shipov.max@icloud.com
