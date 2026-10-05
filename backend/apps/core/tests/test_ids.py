import itertools
import time
import uuid

from apps.core.ids import uuid7


def test_returns_uuid7():
    """Test that uuid7 returns a valid UUIDv7."""
    u = uuid7()
    assert isinstance(u, uuid.UUID)
    assert u.version == 7


def test_timestamp_is_now():
    """Test that the timestamp in a UUIDv7 is the current time."""
    before = time.time_ns() // 1_000_000
    u = uuid7()
    after = time.time_ns() // 1_000_000
    assert before <= u.time <= after


def test_consecutive_ids_increase():
    """Every ID sorts after the previous one, even within the same millisecond."""
    ids = [uuid7() for _ in range(10_000)]
    assert all(a < b for a, b in itertools.pairwise(ids))


def test_unique():
    """Test that uuid7 generates unique UUIDs."""
    ids = {uuid7() for _ in range(10_000)}
    assert len(ids) == 10_000
