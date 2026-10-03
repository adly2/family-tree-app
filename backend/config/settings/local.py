"""
Development settings.

Why DEBUG lives here instead of in base.py, defaulting to False there:

The tempting one-liner is

    DEBUG = env.bool("DJANGO_DEBUG", default=True)

in a single settings.py. That fails OPEN. Forget the variable on a production
server and Django serves full stack traces -- including environment variables,
SQL queries, and settings values -- to anyone who triggers an error.

Defaulting to False and opting in here inverts the failure mode. Misconfigure
it and development merely looks like production: no debug toolbar, unhelpful
error pages. Annoying, and you notice in seconds. The other way round, you
leak your SECRET_KEY to the internet and may never notice.

Run with:  uv run manage.py runserver
(manage.py already points DJANGO_SETTINGS_MODULE here.)
"""

from .base import *  # noqa: F403

DEBUG = env.bool("DJANGO_DEBUG", default=True)  # noqa: F405

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
