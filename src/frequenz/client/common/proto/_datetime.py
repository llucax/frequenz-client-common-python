# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Helper functions to convert protobuf Timestamp <-> Python datetime."""

from datetime import datetime, timedelta, timezone
from typing import overload

from google.protobuf import timestamp_pb2
from typing_extensions import deprecated

from .._datetime import InvalidDatetime

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
"""The Unix epoch, the instant a protobuf `Timestamp` counts seconds from."""

_MAX_NANOS = 999_999_999
"""The largest fraction of a second a protobuf `Timestamp` may carry."""


@overload
def datetime_to_proto(dt: datetime) -> timestamp_pb2.Timestamp:
    """Convert a datetime to a protobuf Timestamp.

    Args:
        dt: The datetime object to convert.

    Returns:
        The datetime converted to a Timestamp.
    """


@overload
def datetime_to_proto(dt: None) -> None:
    """Return `None` for a `None` input.

    Args:
        dt: None

    Returns:
        None
    """


def datetime_to_proto(dt: datetime | None) -> timestamp_pb2.Timestamp | None:
    """Convert a datetime to a protobuf Timestamp.

    Args:
        dt: The datetime object to convert.

    Returns:
        The datetime converted to a Timestamp, or `None` if `dt` is `None`.
    """
    if dt is None:
        return None

    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(dt)
    return ts


@deprecated(
    "frequenz.client.common.proto.datetime_from_proto is deprecated since "
    "v0.4.1. Use [frequenz.client.common.proto.datetime_from_proto2][] instead."
)
def datetime_from_proto(  # noqa: DOC502
    ts: timestamp_pb2.Timestamp, tz: timezone = timezone.utc
) -> datetime:
    """Convert a protobuf Timestamp to a datetime.

    [`datetime_from_proto2`][..datetime_from_proto2] keeps a malformed
    timestamp in its return type (`datetime | InvalidDatetime`) rather than
    raising or silently repairing it, and is exact across the whole protobuf
    range, where this function loses sub-second precision far from the epoch.
    It always returns UTC; call [`astimezone()`][datetime.datetime.astimezone]
    on the result instead of passing `tz`.

    Args:
        ts: The Timestamp object to convert.
        tz: The timezone to use for the datetime.

    Returns:
        The Timestamp converted to a datetime.

    Raises:
        ValueError: If the timestamp has no [`datetime`][datetime.datetime]
            equivalent in `tz`.
        OverflowError: If the timestamp is so far from the epoch that the
            conversion itself overflows.
        OSError: If the underlying platform call fails.
    """
    # Add microseconds and add nanoseconds converted to microseconds
    microseconds = int(ts.nanos / 1000)
    return datetime.fromtimestamp(ts.seconds + microseconds * 1e-6, tz=tz)


def datetime_from_proto2(
    ts: timestamp_pb2.Timestamp,
) -> datetime | InvalidDatetime:
    """Convert a protobuf Timestamp to a UTC datetime, preserving invalid data.

    A protobuf `Timestamp` is a `seconds` count since the Unix epoch plus a
    `nanos` fraction. Both are plain integers on the wire, so a decoded message
    can carry values the `Timestamp` contract does not allow. This function
    keeps those in its return type instead of raising, so the caller still
    receives what the server sent.

    A timestamp is well-formed when `seconds` is in
    `[-62135596800, 253402300799]` — the years 1 to 9999 — and `nanos` is in
    `[0, 999999999]`. That `seconds` range is exactly the range
    [`datetime`][datetime.datetime] covers, so every well-formed timestamp has
    a UTC [`datetime`][datetime.datetime]. The `nanos` fraction is truncated to
    the microsecond resolution of [`datetime`][datetime.datetime].

    An out-of-range `nanos` is not carried over into `seconds`. The `Timestamp`
    contract does not allow it, so its intended meaning is unknown, and
    guessing one would hand the caller a plausible-looking timestamp built from
    data the sender never promised.

    Note:
        The result is always in UTC, which is what a `Timestamp` denotes. Call
        [`astimezone()`][datetime.datetime.astimezone] on it for another zone.
        That conversion can itself overflow within a day of either end of the
        range, which is why it is left to the caller rather than hidden in a
        `tz` argument here.

    Args:
        ts: The Timestamp object to convert.

    Returns:
        The Timestamp converted to a UTC datetime, or an
            [`InvalidDatetime`][frequenz.client.common.InvalidDatetime]
            carrying the raw `seconds` and `nanos` when the timestamp is not
            well-formed.
    """
    seconds = ts.seconds
    nanos = ts.nanos
    if not 0 <= nanos <= _MAX_NANOS:
        return InvalidDatetime(seconds=seconds, nanos=nanos)
    try:
        # Going through `timedelta` instead of `datetime.fromtimestamp()` keeps
        # the conversion exact: a `float` timestamp cannot hold microsecond
        # resolution across the whole protobuf range.
        return _EPOCH + timedelta(seconds=seconds, microseconds=nanos // 1000)
    except OverflowError:
        return InvalidDatetime(seconds=seconds, nanos=nanos)
