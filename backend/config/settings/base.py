"""
Settings shared by every environment.

Nothing in this file may assume it is running in development. Anything that
differs between dev and production belongs in local.py or production.py.
"""

from pathlib import Path

import environ

# This file is config/settings/base.py, so three parents up is backend/ --
# the directory holding manage.py.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# One more level up is the repository root, where .env and docker-compose.yml
# live. The database credentials are shared with Compose, so there is exactly
# one .env and it sits above backend/.
REPO_ROOT = BASE_DIR.parent

env = environ.Env()
environ.Env.read_env(REPO_ROOT / ".env")

# Deliberately no default. A missing SECRET_KEY must crash at startup rather
# than silently fall back to something guessable.
SECRET_KEY = env("DJANGO_SECRET_KEY")

# False here, overridden to True in local.py. See the note in that file -- this
# direction is a security decision, not a style choice.
DEBUG = False
ALLOWED_HOSTS: list[str] = []


# --- Applications ---------------------------------------------------------
# Django's plugin registry. Each entry is a package that may contribute models,
# migrations, admin pages, templates, and management commands.

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS: list[str] = []
# Ours, added as each is created. accounts arrives in unit 5.
LOCAL_APPS: list[str] = []

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# --- Middleware -----------------------------------------------------------
# An ordered pipeline: requests pass down this list, responses back up it.
# Order is load-bearing. SessionMiddleware must precede AuthenticationMiddleware
# because the latter builds request.user by reading the session.

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        # Load templates from each installed app's templates/ directory.
        # This is how the admin finds its own templates.
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# --- Database -------------------------------------------------------------
# Credentials come from the repo-root .env, shared with docker-compose.yml.
DATABASES: dict = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env.int("POSTGRES_PORT"),
    }
}


# --- Authentication -------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internationalization -------------------------------------------------

LANGUAGE_CODE = "en-us"
# Timestamps are stored in UTC and converted at the edges. Note that this has
# nothing to do with genealogical dates ("circa 1890"), which are a separate
# modeling problem in Phase 1.
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --- Static files ---------------------------------------------------------

STATIC_URL = "static/"
# Where `collectstatic` gathers files for a real web server to serve. Unused
# by runserver; needed from Phase 9.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Only applies to models that do not declare a primary key. Ours all use
# UUIDv7 from apps.core.ids, so this is a fallback for third-party models.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
