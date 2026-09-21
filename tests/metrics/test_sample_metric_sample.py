# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for MetricSample class."""

from datetime import datetime, timezone

import pytest
from frequenz.core.typing import FloatInt

from frequenz.client.common import (
    InvalidDatetime,
    InvalidDatetimeError,
    UnrecognizedEnumValueError,
    UnspecifiedEnumValueError,
)
from frequenz.client.common.metrics import (
    AggregatedMetricValue,
    AggregationMethod,
    Bounds,
    BoundsSet,
    InvalidBounds,
    InvalidBoundsSet,
    InvalidBoundsSetError,
    Metric,
    MetricConnection,
    MetricConnectionCategory,
    MetricSample,
)


@pytest.fixture
def now() -> datetime:
    """Get the current time."""
    return datetime.now(timezone.utc)


@pytest.mark.parametrize(
    "value,connection",
    [
        pytest.param(
            5.0,
            None,
            id="simple_value",
        ),
        pytest.param(
            AggregatedMetricValue(
                avg=5.0,
                min=1.0,
                max=10.0,
                raw=[1.0, 5.0, 10.0],
            ),
            "dc_battery_0",
            id="aggregated_value",
        ),
        pytest.param(
            None,
            None,
            id="none_value",
        ),
    ],
)
def test_creation(
    now: datetime,
    value: FloatInt | AggregatedMetricValue | None,
    connection: MetricConnection | None,
) -> None:
    """Test MetricSample creation with different value types."""
    bounds_set = BoundsSet(bounds=(Bounds(lower=-10.0, upper=10.0),))
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=value,
        bounds_set=bounds_set,
        connection=connection,
    )
    assert sample.sample_time2 == now
    assert sample.metric == Metric.AC_POWER_ACTIVE
    assert sample.value == value
    assert sample.bounds_set == bounds_set
    assert sample.connection == connection


@pytest.mark.parametrize(
    "metric, value, connection, expected",
    [
        pytest.param(
            Metric.AC_POWER_ACTIVE,
            5.0,
            None,
            "AC_POWER_ACTIVE=5.0",
            id="known_metric",
        ),
        pytest.param(
            Metric.AC_POWER_ACTIVE,
            5.0,
            MetricConnection(
                category=MetricConnectionCategory.BATTERY, name="dc_battery_0"
            ),
            "AC_POWER_ACTIVE=5.0@dc_battery_0:BATTERY",
            id="with_connection",
        ),
        pytest.param(
            0,
            None,
            None,
            "<invalid:0>=None",
            id="unspecified_metric",
        ),
        pytest.param(
            99999,
            42,
            None,
            "99999=42",
            id="unrecognized_metric",
        ),
        pytest.param(
            Metric.AC_POWER_ACTIVE,
            AggregatedMetricValue(avg=5.0, min=1.0, max=10.0, raw=[1.0, 5.0, 10.0]),
            None,
            "AC_POWER_ACTIVE=avg:5.0<min:1.0 max:10.0 num_raw:3>",
            id="aggregated_value",
        ),
    ],
)
def test_str(
    now: datetime,
    metric: Metric | int,
    value: FloatInt | AggregatedMetricValue | None,
    connection: MetricConnection | None,
    expected: str,
) -> None:
    """`MetricSample.__str__` renders a compact `metric=value` summary."""
    sample = MetricSample(
        sample_time=now,
        metric=metric,
        value=value,
        bounds_set=BoundsSet(),
        connection=connection,
    )
    assert str(sample) == expected


@pytest.mark.parametrize(
    "value, method_results",
    [
        pytest.param(
            5.0,
            {
                AggregationMethod.AVG: 5.0,
                AggregationMethod.MIN: 5.0,
                AggregationMethod.MAX: 5.0,
            },
            id="simple_value",
        ),
        pytest.param(
            AggregatedMetricValue(
                avg=5.0,
                min=1.0,
                max=10.0,
                raw=[1.0, 5.0, 10.0],
            ),
            {
                AggregationMethod.AVG: 5.0,
                AggregationMethod.MIN: 1.0,
                AggregationMethod.MAX: 10.0,
            },
            id="aggregated_value",
        ),
        pytest.param(
            None,
            {
                AggregationMethod.AVG: None,
                AggregationMethod.MIN: None,
                AggregationMethod.MAX: None,
            },
            id="none_value",
        ),
        pytest.param(
            5,
            {
                AggregationMethod.AVG: 5,
                AggregationMethod.MIN: 5,
                AggregationMethod.MAX: 5,
            },
            id="simple_int_value",
        ),
        pytest.param(
            AggregatedMetricValue(avg=5, min=1, max=10, raw=[1, 5, 10]),
            {
                AggregationMethod.AVG: 5,
                AggregationMethod.MIN: 1,
                AggregationMethod.MAX: 10,
            },
            id="aggregated_int_value",
        ),
    ],
)
def test_as_single_value(
    now: datetime,
    value: FloatInt | AggregatedMetricValue | None,
    method_results: dict[AggregationMethod, FloatInt | None],
) -> None:
    """Test MetricSample.as_single_value with different value types and methods."""
    bounds_set = BoundsSet(bounds=(Bounds(lower=-10.0, upper=10.0),))

    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=value,
        bounds_set=bounds_set,
    )

    for method, expected in method_results.items():
        assert sample.as_single_value(aggregation_method=method) == expected


def test_as_single_value_returns_int_untouched(now: datetime) -> None:
    """An `int` value is returned as is, without coercion to `float`."""
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=5,
        bounds_set=BoundsSet(),
    )
    result = sample.as_single_value()
    assert result == 5
    assert type(result) is int  # pylint: disable=unidiomatic-typecheck


def test_multiple_bounds(now: datetime) -> None:
    """Test MetricSample creation with multiple bounds."""
    bounds_set = BoundsSet(
        bounds=(
            Bounds(lower=-10.0, upper=-5.0),
            Bounds(lower=5.0, upper=10.0),
        )
    )
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=7.0,
        bounds_set=bounds_set,
    )
    assert sample.bounds_set == bounds_set


def test_deprecated_bounds_kwarg(now: datetime) -> None:
    """The deprecated `bounds` argument builds a `BoundsSet` and warns."""
    with pytest.deprecated_call():
        sample = MetricSample(
            sample_time=now,
            metric=Metric.AC_POWER_ACTIVE,
            value=5.0,
            bounds=[Bounds(lower=-10.0, upper=10.0)],
        )
    assert sample.bounds_set == BoundsSet(bounds=(Bounds(lower=-10.0, upper=10.0),))


def test_deprecated_bounds_property(now: datetime) -> None:
    """The deprecated `bounds` property returns the valid bounds and warns."""
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=BoundsSet(bounds=(Bounds(lower=-10.0, upper=10.0),)),
    )
    with pytest.deprecated_call():
        assert sample.bounds == [Bounds(lower=-10.0, upper=10.0)]


def test_deprecated_bounds_property_normalizes_invalid_set(now: datetime) -> None:
    """The deprecated `bounds` property returns normalized valid bounds for an invalid set."""
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=InvalidBoundsSet(
            bounds=(
                Bounds(lower=1.0, upper=5.0),
                Bounds(lower=3.0, upper=8.0),  # overlaps the previous -> merged
                InvalidBounds(lower=10.0, upper=-10.0),  # dropped
            )
        ),
    )
    with pytest.deprecated_call():
        assert sample.bounds == [Bounds(lower=1.0, upper=8.0)]


def test_bounds_and_bounds_set_raises(now: datetime) -> None:
    """Passing both `bounds` and `bounds_set` raises `TypeError`."""
    with pytest.raises(TypeError, match="not both"):
        MetricSample(
            sample_time=now,
            metric=Metric.AC_POWER_ACTIVE,
            value=5.0,
            bounds=[Bounds(lower=-10.0, upper=10.0)],
            bounds_set=BoundsSet(),
        )


def test_missing_bounds_set_raises(now: datetime) -> None:
    """Passing neither `bounds` nor `bounds_set` raises `TypeError`."""
    with pytest.raises(TypeError, match="requires the"):
        MetricSample(
            sample_time=now,
            metric=Metric.AC_POWER_ACTIVE,
            value=5.0,
        )


def test_get_metric_returns_known_member(now: datetime) -> None:
    """get_metric returns the metric when it is a known member."""
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=None,
        bounds_set=BoundsSet(),
    )
    assert sample.get_metric() is Metric.AC_POWER_ACTIVE


def test_get_metric_unspecified_int_raises(now: datetime) -> None:
    """get_metric raises UnspecifiedEnumValueError for the raw int 0."""
    sample = MetricSample(sample_time=now, metric=0, value=None, bounds_set=BoundsSet())
    with pytest.raises(UnspecifiedEnumValueError):
        sample.get_metric()


def test_get_metric_unspecified_member_raises(now: datetime) -> None:
    """get_metric raises UnspecifiedEnumValueError for the value-0 member."""
    with pytest.deprecated_call():
        sample = MetricSample(
            sample_time=now,
            metric=Metric.UNSPECIFIED,
            value=None,
            bounds_set=BoundsSet(),
        )
    with pytest.raises(UnspecifiedEnumValueError):
        sample.get_metric()


def test_get_metric_unrecognized_int_raises(now: datetime) -> None:
    """get_metric raises UnrecognizedEnumValueError carrying the raw int value."""
    sample = MetricSample(
        sample_time=now, metric=99999, value=None, bounds_set=BoundsSet()
    )
    with pytest.raises(UnrecognizedEnumValueError) as exc_info:
        sample.get_metric()
    assert exc_info.value.value == 99999


def test_get_bounds_set_returns_valid(now: datetime) -> None:
    """get_bounds_set returns the set when it is a valid BoundsSet."""
    bounds_set = BoundsSet(bounds=(Bounds(lower=-10.0, upper=10.0),))
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=bounds_set,
    )
    assert sample.get_bounds_set() is bounds_set


def test_get_bounds_set_invalid_raises(now: datetime) -> None:
    """get_bounds_set raises InvalidBoundsSetError for an InvalidBoundsSet."""
    invalid = InvalidBoundsSet(bounds=(InvalidBounds(lower=10.0, upper=-10.0),))
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=invalid,
    )
    with pytest.raises(InvalidBoundsSetError) as exc_info:
        sample.get_bounds_set()
    assert exc_info.value.bounds_set is invalid


def test_get_sample_time_returns_valid(now: datetime) -> None:
    """get_sample_time returns the time when it is a valid datetime."""
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=BoundsSet(),
    )
    assert sample.get_sample_time() is now


def test_get_sample_time_invalid_raises() -> None:
    """get_sample_time raises InvalidDatetimeError for an InvalidDatetime."""
    invalid = InvalidDatetime(seconds=253402300800, nanos=0)
    sample = MetricSample(
        sample_time2=invalid,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=BoundsSet(),
    )
    assert sample.sample_time2 is invalid
    with pytest.raises(InvalidDatetimeError) as exc_info:
        sample.get_sample_time()
    assert exc_info.value.datetime is invalid
    assert exc_info.value.attr_name == "sample_time2"


def test_deprecated_sample_time_property(now: datetime) -> None:
    """The deprecated `sample_time` property still returns the valid datetime."""
    sample = MetricSample(
        sample_time=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=BoundsSet(),
    )
    assert sample.sample_time2 is now
    with pytest.deprecated_call(
        match=(
            r"^frequenz\.client\.common\.metrics\.MetricSample\.sample_time is "
            r"deprecated since v0\.4\.1\. Use "
            r"\[frequenz\.client\.common\.metrics\.MetricSample\.get_sample_time\]"
            r"\[\] instead\.$"
        )
    ):
        assert sample.sample_time is now


def test_deprecated_sample_time_property_raises_for_invalid() -> None:
    """The deprecated property cannot express an `InvalidDatetime`, so it raises."""
    invalid = InvalidDatetime(seconds=253402300800, nanos=0)
    sample = MetricSample(
        sample_time2=invalid,
        metric=Metric.AC_POWER_ACTIVE,
        value=5.0,
        bounds_set=BoundsSet(),
    )
    with pytest.deprecated_call(), pytest.raises(InvalidDatetimeError):
        _ = sample.sample_time


def test_sample_time_and_sample_time2_raises(now: datetime) -> None:
    """Passing both spellings of the sample time is an error."""
    with pytest.raises(
        TypeError,
        match=r"accepts either `sample_time` or `sample_time2`, not both",
    ):
        MetricSample(
            sample_time=now,
            sample_time2=now,
            metric=Metric.AC_POWER_ACTIVE,
            value=5.0,
            bounds_set=BoundsSet(),
        )


def test_missing_sample_time_raises() -> None:
    """Passing neither spelling of the sample time is an error."""
    with pytest.raises(TypeError, match=r"requires the `sample_time2` argument"):
        MetricSample(  # pylint: disable=missing-kwoa
            metric=Metric.AC_POWER_ACTIVE,
            value=5.0,
            bounds_set=BoundsSet(),
        )
