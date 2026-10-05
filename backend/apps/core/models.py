from uuid import uuid7

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
