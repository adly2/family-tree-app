import secrets
import time
import uuid

import pytest

from apps.core.ids import uuid7, uuid7_timestamp_ms


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
    timestamp = uuid7_timestamp_ms(u)
    assert before <= timestamp <= after


def test_explicit_timestamp():
    """Test that uuid7 works with an explicit timestamp."""
    timestamp = 12
    u = uuid7(timestamp_ms=timestamp)
    assert uuid7_timestamp_ms(u) == timestamp


def test_later_time_sorts_after():
    """Test that a UUIDv7 with a later timestamp sorts after one with an earlier timestamp."""
    u1 = uuid7(timestamp_ms=10)
    u2 = uuid7(timestamp_ms=11)
    assert u1 < u2


def test_unique():
    """Test that uuid7 generates unique UUIDs."""
    ids = {uuid7() for _ in range(10_000)}
    assert len(ids) == 10_000


def test_exact_layout(monkeypatch):
    """With all random bits zero, only the timestamp, version, and variant remain."""
    monkeypatch.setattr(secrets, "randbits", lambda k: 0)
    assert uuid7(timestamp_ms=1).int == (1 << 80) | (0b0111 << 76) | (0 << 64) | (0b10 << 62)


def test_exact_layout_all_ones(monkeypatch):
    """With all random bits set, a too-wide random field would clobber version or variant."""
    monkeypatch.setattr(secrets, "randbits", lambda k: (1 << k) - 1)
    expected = (1 << 80) | (0b0111 << 76) | (0xFFF << 64) | (0b10 << 62) | ((1 << 62) - 1)
    assert uuid7(timestamp_ms=1).int == expected


def test_rejects_out_of_range_timestamp():
    """A timestamp outside 48 bits would spill into the version bits."""
    with pytest.raises(ValueError, match="timestamp"):
        uuid7(timestamp_ms=-1)
    with pytest.raises(ValueError, match="timestamp"):
        uuid7(timestamp_ms=1 << 48)
