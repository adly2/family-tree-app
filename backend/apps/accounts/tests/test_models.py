import pytest
from django.db import IntegrityError

from apps.accounts.models import User


@pytest.mark.django_db
def test_new_users_get_distinct_uuid7_ids():
    """Test that new users get distinct UUIDv7 IDs."""
    user1 = User.objects.create_user(username="user1", email="user1@example.com")
    user2 = User.objects.create_user(username="user2", email="user2@example.com")

    assert user1.id.version == 7
    assert user2.id.version == 7
    assert user1.id != user2.id


@pytest.mark.django_db
def test_duplicate_email_is_rejected():
    """Test that duplicate emails are rejected."""
    User.objects.create_user(username="user1", email="user1@example.com")

    with pytest.raises(IntegrityError):
        User.objects.create_user(username="user2", email="user1@example.com")
