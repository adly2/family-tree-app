"""
Production settings.

Mostly empty until Phase 9. It exists now so that production-only values are
never quietly defaulted in base.py, and so the split is visible from day one.

Phase 9 adds: SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE,
SECURE_HSTS_SECONDS, structured logging, and a real static-file strategy.
"""

from .base import *  # noqa: F403

DEBUG = False

# No default: a production deploy must state its hostnames explicitly.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # noqa: F405
