import secrets
import time
import uuid


def uuid7(timestamp_ms: int | None = None) -> uuid.UUID:
    """Return a new UUIDv7. Uses the current time unless timestamp_ms is given."""
    if timestamp_ms is None:  # Use the current time
        timestamp_ms = int(time.time_ns() // 1000000)
    elif timestamp_ms < 0 or timestamp_ms >= (1 << 48):
        raise ValueError("Invalid timestamp")
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)
    var = 0b10
    ver = 0b0111
    uuid_int = timestamp_ms << 80 | ver << 76 | rand_a << 64 | var << 62 | rand_b
    return uuid.UUID(int=uuid_int)


def uuid7_timestamp_ms(value: uuid.UUID) -> int:
    """Return the millisecond timestamp stored in the top 48 bits of a UUIDv7."""
    return int(value) >> 80
