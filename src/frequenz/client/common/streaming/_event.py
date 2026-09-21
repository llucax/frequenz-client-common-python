# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Streaming event type enum."""

from frequenz.core.enum import Enum, deprecated_member, unique


@unique
class Event(Enum):
    """A type of streaming event."""

    UNSPECIFIED = deprecated_member(
        0,
        "frequenz.client.common.streaming.Event.UNSPECIFIED is deprecated "
        "since v0.4.1. Use the int value 0 instead if you really need to check "
        "for this low-level value.",
    )
    """Unspecified event type."""

    CREATED = 1
    """Event when a new resource is created."""

    UPDATED = 2
    """Event when an existing resource is updated."""

    DELETED = 3
    """Event when a resource is deleted."""
