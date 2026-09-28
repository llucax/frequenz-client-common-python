# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for MetricSample protobuf conversion."""

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final

import pytest
from frequenz.api.common.v1alpha8.metrics import bounds_pb2, metrics_pb2
from frequenz.core.warnings import asserting_no_deprecations
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.common import InvalidDatetime, InvalidDatetimeError
from frequenz.client.common.metrics import (
    AggregatedMetricValue,
    Bounds,
    BoundsSet,
    InvalidBounds,
    InvalidBoundsSet,
    Metric,
    MetricConnection,
    MetricConnectionCategory,
    MetricSample,
)
from frequenz.client.common.metrics.proto.v1alpha8 import (
    metric_connection_category_to_proto,
    metric_sample_from_proto,
    metric_sample_from_proto_with_issues,
    metric_to_proto,
)

DATETIME: Final[datetime] = datetime(2023, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
TIMESTAMP: Final[Timestamp] = Timestamp(seconds=int(DATETIME.timestamp()))


@dataclass(frozen=True, kw_only=True)
class _TestCase:
    """Test case for MetricSample protobuf conversion."""

    name: str
    """The description of the test case."""

    proto_message: metrics_pb2.MetricSample
    """The input protobuf message."""

    expected_sample: MetricSample
    """The expected MetricSample object."""

    expected_major_issues: list[str] = field(default_factory=list)
    """Expected major issues during conversion."""

    expected_minor_issues: list[str] = field(default_factory=list)
    """Expected minor issues during conversion."""


@pytest.mark.parametrize(
    "case",
    [
        _TestCase(
            name="simple_value",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds_set=BoundsSet(),
                connection=None,
            ),
        ),
        _TestCase(
            name="aggregated_value",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                value=metrics_pb2.MetricValueVariant(
                    aggregated_metric=metrics_pb2.AggregatedMetricValue(
                        avg_value=5.0, min_value=1.0, max_value=10.0
                    )
                ),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=AggregatedMetricValue(avg=5.0, min=1.0, max=10.0, raw=[]),
                bounds_set=BoundsSet(),
                connection=None,
            ),
        ),
        _TestCase(
            name="no_value",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=None,
                bounds_set=BoundsSet(),
                connection=None,
            ),
        ),
        _TestCase(
            name="unrecognized_metric",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=999,  # type: ignore[arg-type]
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=999,
                value=5.0,
                bounds_set=BoundsSet(),
                connection=None,
            ),
        ),
        _TestCase(
            name="with_valid_bounds",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
                bounds=[bounds_pb2.Bounds(lower=-10.0, upper=10.0)],
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds_set=BoundsSet(bounds=(Bounds(lower=-10.0, upper=10.0),)),
                connection=None,
            ),
        ),
        _TestCase(
            name="with_invalid_bounds",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
                bounds=[
                    bounds_pb2.Bounds(lower=-10.0, upper=10.0),
                    bounds_pb2.Bounds(lower=10.0, upper=-10.0),  # Invalid
                ],
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds_set=InvalidBoundsSet(
                    bounds=(
                        Bounds(lower=-10.0, upper=10.0),
                        InvalidBounds(lower=10.0, upper=-10.0),
                    )
                ),
                connection=None,
            ),
        ),
        _TestCase(
            name="with_connection",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
                connection=metrics_pb2.MetricConnection(
                    category=metric_connection_category_to_proto(
                        MetricConnectionCategory.BATTERY
                    ),
                    name="dc_battery_0",
                ),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds_set=BoundsSet(),
                connection=MetricConnection(
                    category=MetricConnectionCategory.BATTERY, name="dc_battery_0"
                ),
            ),
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto_with_issues(case: _TestCase) -> None:
    """Test conversion from protobuf message to MetricSample."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    # The timestamp in the expected sample needs to match the one from proto conversion
    # We use a fixed timestamp in test cases, so this is fine.
    # If dynamic timestamps were used, we'd need to adjust here or in the fixture.

    with pytest.deprecated_call(match="metric_sample_from_proto"):
        sample = metric_sample_from_proto_with_issues(
            case.proto_message,
            major_issues=major_issues,
            minor_issues=minor_issues,
        )

    assert sample == case.expected_sample
    assert major_issues == case.expected_major_issues
    assert minor_issues == case.expected_minor_issues


def test_with_unspecified_metric() -> None:
    """Test the deprecated converter stores an unspecified metric as int 0.

    The dataclass-level converter stores the raw int ``0`` for an unspecified
    metric (never the deprecated member).
    """
    proto = metrics_pb2.MetricSample(
        sample_time=TIMESTAMP,
        metric=metrics_pb2.Metric.METRIC_UNSPECIFIED,
        value=metrics_pb2.MetricValueVariant(
            simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
        ),
    )

    major_issues: list[str] = []
    minor_issues: list[str] = []

    with pytest.deprecated_call(match="metric_sample_from_proto"):
        sample = metric_sample_from_proto_with_issues(
            proto, major_issues=major_issues, minor_issues=minor_issues
        )

    assert sample.metric == 0
    assert not isinstance(sample.metric, Metric)
    assert not major_issues
    assert not minor_issues


@pytest.mark.parametrize(
    "lower, upper",
    [
        (math.nan, 10.0),
        (-10.0, math.nan),
        (math.nan, math.nan),
    ],
    ids=["lower", "upper", "both"],
)
def test_with_nan_bounds(lower: float, upper: float) -> None:
    """A `NaN` bound endpoint is preserved as an `InvalidBoundsSet`."""
    proto = metrics_pb2.MetricSample(
        sample_time=TIMESTAMP,
        metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
        value=metrics_pb2.MetricValueVariant(
            simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
        ),
        bounds=[bounds_pb2.Bounds(lower=lower, upper=upper)],
    )

    major_issues: list[str] = []
    minor_issues: list[str] = []

    with pytest.deprecated_call(match="metric_sample_from_proto"):
        sample = metric_sample_from_proto_with_issues(
            proto, major_issues=major_issues, minor_issues=minor_issues
        )

    assert isinstance(sample.bounds_set, InvalidBoundsSet)


@pytest.mark.parametrize(
    "case",
    [
        _TestCase(
            name="simple_value",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds_set=BoundsSet(),
                connection=None,
            ),
        ),
        _TestCase(
            name="unrecognized_metric",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=999,  # type: ignore[arg-type]
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=999,
                value=5.0,
                bounds_set=BoundsSet(),
                connection=None,
            ),
        ),
        _TestCase(
            name="invalid_bounds",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                bounds=[bounds_pb2.Bounds(lower=10.0, upper=-10.0)],  # Invalid
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=None,
                bounds_set=InvalidBoundsSet(
                    bounds=(InvalidBounds(lower=10.0, upper=-10.0),)
                ),
                connection=None,
            ),
        ),
        _TestCase(
            name="with_connection",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
                connection=metrics_pb2.MetricConnection(
                    category=metric_connection_category_to_proto(
                        MetricConnectionCategory.BATTERY
                    ),
                    name="dc_battery_0",
                ),
            ),
            expected_sample=MetricSample(
                sample_time=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=None,
                bounds_set=BoundsSet(),
                connection=MetricConnection(
                    category=MetricConnectionCategory.BATTERY, name="dc_battery_0"
                ),
            ),
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto(case: _TestCase) -> None:
    """Test conversion from protobuf message to MetricSample via the sister."""
    sample = metric_sample_from_proto(case.proto_message)
    assert sample == case.expected_sample


def test_from_proto_unspecified_metric() -> None:
    """An unspecified metric is stored as int 0 without warning."""
    proto = metrics_pb2.MetricSample(
        sample_time=TIMESTAMP,
        metric=metrics_pb2.Metric.METRIC_UNSPECIFIED,
        value=metrics_pb2.MetricValueVariant(
            simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
        ),
    )

    with asserting_no_deprecations():
        sample = metric_sample_from_proto(proto)

    assert sample.metric == 0
    assert not isinstance(sample.metric, Metric)


def _sample_with_time(sample_time: Timestamp) -> metrics_pb2.MetricSample:
    """Build a minimal well-formed sample carrying the given time.

    Args:
        sample_time: The timestamp to put in the `sample_time` field.

    Returns:
        The protobuf message.
    """
    return metrics_pb2.MetricSample(
        sample_time=sample_time,
        metric=metric_to_proto(Metric.AC_POWER_ACTIVE),
        value=metrics_pb2.MetricValueVariant(
            simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
        ),
    )


@pytest.mark.parametrize(
    "sample_time",
    [
        pytest.param(Timestamp(seconds=253402300800), id="year-10000"),
        pytest.param(Timestamp(seconds=-62135596801), id="before-year-1"),
        pytest.param(Timestamp(seconds=0, nanos=-1), id="negative-nanos"),
        pytest.param(Timestamp(seconds=0, nanos=1000000000), id="a-whole-second"),
    ],
)
def test_from_proto_unrepresentable_sample_time(sample_time: Timestamp) -> None:
    """An unrepresentable sample time is preserved instead of raising."""
    sample = metric_sample_from_proto(_sample_with_time(sample_time))

    assert sample.sample_time2 == InvalidDatetime(
        seconds=sample_time.seconds, nanos=sample_time.nanos
    )
    with pytest.raises(InvalidDatetimeError):
        sample.get_sample_time()


def test_from_proto_with_issues_malformed_sample_time_raises() -> None:
    """The released converter keeps raising, as it did before the union."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    with (
        pytest.deprecated_call(match="metric_sample_from_proto"),
        pytest.raises(
            ValueError, match=r"malformed sample_time <invalid:253402300800s\+0ns>"
        ),
    ):
        metric_sample_from_proto_with_issues(
            _sample_with_time(Timestamp(seconds=253402300800)),
            major_issues=major_issues,
            minor_issues=minor_issues,
        )
