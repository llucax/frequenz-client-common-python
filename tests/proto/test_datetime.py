# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Test conversion helper functions."""

from datetime import datetime, timedelta, timezone

import pytest

# pylint: disable=no-name-in-module
from google.protobuf.timestamp_pb2 import Timestamp

# pylint: enable=no-name-in-module
from hypothesis import given
from hypothesis import strategies as st

from frequenz.client.common import InvalidDatetime
from frequenz.client.common.proto import (
    datetime_from_proto,
    datetime_from_proto2,
    datetime_to_proto,
)

# The oldest and newest instants both protobuf and Python can represent.
_MIN_SECONDS = -62135596800  # 0001-01-01T00:00:00Z
_MAX_SECONDS = 253402300799  # 9999-12-31T23:59:59Z
_MAX_NANOS = 999999999

# Strategy for generating datetime objects
# It requires naive datetime objects because it creates the timezone via a strategy
datetime_strategy = st.datetimes(
    min_value=datetime(1970, 1, 1),  # noqa: DTZ001
    max_value=datetime(9999, 12, 31),  # noqa: DTZ001
    timezones=st.just(timezone.utc),
)

# Strategy for generating Timestamp objects
timestamp_strategy = st.builds(
    Timestamp,
    seconds=st.integers(
        min_value=0,
        max_value=int(datetime(9999, 12, 31, tzinfo=timezone.utc).timestamp()),
    ),
)


@given(datetime_strategy)
def test_to_timestamp_with_datetime(dt: datetime) -> None:
    """Test conversion from datetime to Timestamp."""
    ts = datetime_to_proto(dt)
    assert ts is not None
    assert datetime_from_proto2(ts) == dt


def test_to_timestamp_with_none() -> None:
    """Test that passing None returns None."""
    assert datetime_to_proto(None) is None


@given(timestamp_strategy)
def test_to_datetime(ts: Timestamp) -> None:
    """Test conversion from Timestamp to datetime."""
    dt = datetime_from_proto2(ts)
    assert isinstance(dt, datetime)
    # Convert back to Timestamp and compare
    converted_back_ts = datetime_to_proto(dt)
    assert ts.seconds == converted_back_ts.seconds


@given(datetime_strategy)
def test_no_none_datetime(dt: datetime) -> None:
    """Test behavior of type hinting."""
    ts: Timestamp = datetime_to_proto(dt)
    dt_none: datetime | None = None

    # The test would fail without the ignore comment as it should.
    ts2: Timestamp = datetime_to_proto(dt_none)  # type: ignore

    assert ts is not None
    assert ts2 is None


def test_from_proto_is_deprecated() -> None:
    """`datetime_from_proto` warns and still converts as it always did."""
    with pytest.deprecated_call(
        match=r"^frequenz\.client\.common\.proto\.datetime_from_proto is "
        r"deprecated since v0\.4\.1\. Use "
        r"\[frequenz\.client\.common\.proto\.datetime_from_proto2\]\[\] instead\.$"
    ):
        converted = datetime_from_proto(Timestamp(seconds=1, nanos=500000000))
    assert converted == datetime(1970, 1, 1, 0, 0, 1, 500000, tzinfo=timezone.utc)


def test_from_proto_still_raises_out_of_range() -> None:
    """`datetime_from_proto` keeps raising, which is why it is deprecated."""
    with pytest.deprecated_call(), pytest.raises((ValueError, OverflowError)):
        datetime_from_proto(Timestamp(seconds=_MAX_SECONDS + 1))


def test_from_proto2_epoch() -> None:
    """An all-zero timestamp is the Unix epoch in UTC."""
    assert datetime_from_proto2(Timestamp()) == datetime(
        1970, 1, 1, tzinfo=timezone.utc
    )


def test_from_proto2_truncates_nanos_to_microseconds() -> None:
    """Sub-microsecond precision is truncated, not rounded."""
    assert datetime_from_proto2(Timestamp(seconds=0, nanos=1999)) == datetime(
        1970, 1, 1, 0, 0, 0, 1, tzinfo=timezone.utc
    )


def test_from_proto2_negative_seconds() -> None:
    """A `nanos` fraction is added to (not subtracted from) negative seconds."""
    assert datetime_from_proto2(Timestamp(seconds=-1, nanos=500000000)) == datetime(
        1969, 12, 31, 23, 59, 59, 500000, tzinfo=timezone.utc
    )


def test_from_proto2_min() -> None:
    """The oldest instant protobuf allows is representable."""
    assert datetime_from_proto2(Timestamp(seconds=_MIN_SECONDS)) == datetime(
        1, 1, 1, tzinfo=timezone.utc
    )


def test_from_proto2_max() -> None:
    """The newest instant protobuf allows is representable, down to the microsecond."""
    assert datetime_from_proto2(
        Timestamp(seconds=_MAX_SECONDS, nanos=_MAX_NANOS)
    ) == datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)


def test_from_proto2_is_always_utc() -> None:
    """The result is aware and in UTC, which is what a `Timestamp` denotes."""
    converted = datetime_from_proto2(Timestamp(seconds=0))
    assert isinstance(converted, datetime)
    assert converted.tzinfo is timezone.utc


def test_from_proto2_result_converts_to_another_zone() -> None:
    """The caller expresses the instant in another zone themselves."""
    tz = timezone(timedelta(hours=5, minutes=30))
    converted = datetime_from_proto2(Timestamp(seconds=0))
    assert isinstance(converted, datetime)
    in_tz = converted.astimezone(tz)
    assert in_tz == converted
    assert (in_tz.hour, in_tz.minute) == (5, 30)


@pytest.mark.parametrize(
    "seconds",
    [
        pytest.param(_MAX_SECONDS + 1, id="above-max"),
        pytest.param(_MIN_SECONDS - 1, id="below-min"),
        pytest.param(2**63 - 1, id="int64-max"),
        pytest.param(-(2**63), id="int64-min"),
    ],
)
def test_from_proto2_seconds_out_of_python_range(seconds: int) -> None:
    """A seconds count outside the years 1 to 9999 is preserved, not raised."""
    assert datetime_from_proto2(Timestamp(seconds=seconds)) == InvalidDatetime(
        seconds=seconds, nanos=0
    )


@pytest.mark.parametrize(
    "nanos",
    [
        pytest.param(-1, id="negative"),
        pytest.param(_MAX_NANOS + 1, id="a-whole-second"),
        pytest.param(-(2**31), id="int32-min"),
        pytest.param(2**31 - 1, id="int32-max"),
    ],
)
def test_from_proto2_nanos_out_of_spec(nanos: int) -> None:
    """A `nanos` fraction outside `[0, 999999999]` is preserved, not normalized."""
    assert datetime_from_proto2(Timestamp(seconds=1, nanos=nanos)) == InvalidDatetime(
        seconds=1, nanos=nanos
    )


def test_from_proto2_out_of_range_survives_the_wire() -> None:
    """A value only a decoded message can carry round-trips into the wrapper."""
    raw = Timestamp(seconds=_MAX_SECONDS + 1, nanos=-1).SerializeToString()
    decoded = Timestamp()
    decoded.ParseFromString(raw)
    assert datetime_from_proto2(decoded) == InvalidDatetime(
        seconds=_MAX_SECONDS + 1, nanos=-1
    )


def test_from_proto2_accepts_every_well_formed_timestamp() -> None:
    """The protobuf `seconds` range is exactly the range `datetime` covers.

    That equality is what lets a single `InvalidDatetime` mean "not a
    well-formed `Timestamp`" without also having to mean "valid but not
    representable".
    """
    for seconds in (_MIN_SECONDS, 0, _MAX_SECONDS):
        for nanos in (0, _MAX_NANOS):
            assert isinstance(
                datetime_from_proto2(Timestamp(seconds=seconds, nanos=nanos)), datetime
            )
