from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import UUIDModel


class User(UUIDModel, AbstractUser):
    email = models.EmailField(unique=True)

    class Meta(AbstractUser.Meta):
        pass
