# Memories Website

A personal memory and tribute website built with Django. It features an animated photo gallery (book-style page-flip), a heartfelt apology page, and a curated home page — all designed to evoke warmth and nostalgia. Content is managed entirely through Django Admin; no code changes are needed to add photos or update messages.

---

## Prerequisites

- Python 3.10 or newer
- pip (comes with Python)

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the values. At minimum, set a strong `SECRET_KEY` for any non-local use. See the comments inside `.env.example` for guidance on each variable.

---

## Database setup

Apply all database migrations to create the required tables:

```bash
python manage.py migrate
```

Create an admin user so you can log in to the Django Admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

---

## Static files

Collect all static assets into `STATIC_ROOT` (required when `DEBUG=False`):

```bash
python manage.py collectstatic
```

Static files are served by [WhiteNoise](https://whitenoise.readthedocs.io/), which handles compression and long-lived cache headers automatically. You do not need a separate static-file server in most deployments.

> In development (`DEBUG=True`) Django serves static files directly from the `static/` source directory, so `collectstatic` is optional unless you are testing production behaviour locally.

---

## Media directory

The `media/` directory stores user-uploaded photos. Create it before running the server if it does not already exist:

```bash
mkdir media
```

Django's `FileSystemStorage` will raise an error on the first upload if this directory is missing.

---

## Running the development server

```bash
python manage.py runserver
```

The site is then available at <http://127.0.0.1:8000/>.  
The admin panel is at <http://127.0.0.1:8000/admin/>.

---

## Running the tests

```bash
python manage.py test memories
```

This runs both the unit tests and property-based tests (powered by [Hypothesis](https://hypothesis.readthedocs.io/)) in the `memories` app.

---

## Production deployment notes

Before starting the server in production, make sure you have:

1. **Set `DEBUG=False`** in `.env` — this disables the debug toolbar and prevents sensitive error details from leaking to visitors.

2. **Set a strong `SECRET_KEY`** — generate a new one with:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Paste the output into `.env` as `SECRET_KEY`.

3. **Set `ALLOWED_HOSTS`** to your domain:
   ```
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

4. **Set `DATABASE_URL`** to a PostgreSQL connection string:
   ```
   DATABASE_URL=postgres://user:password@host:5432/dbname
   ```
   Leave it blank to use the default SQLite database (not recommended for production).

5. **Run migrations** against your production database:
   ```bash
   python manage.py migrate
   ```

6. **Run `collectstatic`** before starting the server — WhiteNoise serves files from `STATIC_ROOT`, which is only populated after this step:
   ```bash
   python manage.py collectstatic --no-input
   ```

7. Start the server with a WSGI server such as Gunicorn:
   ```bash
   gunicorn config.wsgi:application
   ```
