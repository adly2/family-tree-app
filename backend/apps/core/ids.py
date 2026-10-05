"""
Primary key generation.

Every model takes its default primary key from here instead of importing from
the uuid module directly, so the implementation can change in exactly one file.

Python 3.14's uuid.uuid7() replaced a hand-written version -- see commit
da9d5a4 for the bit layout. The built-in also guarantees ordering within a
single millisecond. For a v7 UUID, `.time` returns its millisecond timestamp.
"""

from uuid import uuid7

__all__ = ["uuid7"]
