from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Django's default "Add user" form asks only for username and password, which
    # would save email as "". Email is unique, so the second such user would hit a
    # duplicate-key error. Asking for it here makes the form require it.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "usable_password", "password1", "password2"),
            },
        ),
    )
