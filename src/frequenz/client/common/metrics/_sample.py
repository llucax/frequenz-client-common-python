# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition to work with metric sample values."""

import warnings
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import assert_never

from frequenz.core.enum import Enum, deprecated_member, unique
from frequenz.core.typing import FloatInt
from typing_extensions import deprecated

from .._datetime import InvalidDatetime, InvalidDatetimeError
from .._exception import UnrecognizedEnumValueError, UnspecifiedEnumValueError
from ._bounds import Bounds, BoundsSet, InvalidBoundsSet, InvalidBoundsSetError
from ._metric import Metric


@unique
class AggregationMethod(Enum):
    """The type of the aggregated value."""

    AVG = "avg"
    """The average value of the metric."""

    MIN = "min"
    """The minimum value of the metric."""

    MAX = "max"
    """The maximum value of the metric."""


@dataclass(frozen=True, kw_only=True)
class AggregatedMetricValue:
    """Encapsulates derived statistical summaries of a single metric.

    The message allows for the reporting of statistical summaries — minimum,
    maximum, and average values - as well as the complete list of individual
    samples if available.

    This message represents derived metrics and contains fields for statistical
    summaries—minimum, maximum, and average values. Individual measurements are
    optional, accommodating scenarios where only subsets of this information
    are available.
    """

    avg: FloatInt
    """The derived average value of the metric."""

    min: FloatInt | None
    """The minimum measured value of the metric."""

    max: FloatInt | None
    """The maximum measured value of the metric."""

    raw: Sequence[FloatInt]
    """All the raw individual values (it might be empty if not provided by the component)."""

    def __str__(self) -> str:
        """Return the short string representation of this instance."""
        extra: list[str] = []
        if self.min is not None:
            extra.append(f"min:{self.min}")
        if self.max is not None:
            extra.append(f"max:{self.max}")
        if len(self.raw) > 0:
            extra.append(f"num_raw:{len(self.raw)}")
        extra_str = f"<{' '.join(extra)}>" if extra else ""
        return f"avg:{self.avg}{extra_str}"


@unique
class MetricConnectionCategory(Enum):
    """The categories of connections from which metrics can be obtained."""

    UNSPECIFIED = deprecated_member(
        0,
        "frequenz.client.common.metrics.MetricConnectionCategory.UNSPECIFIED "
        "is deprecated since v0.4.1. Use the int value 0 instead if you really "
        "need to check for this low-level value.",
    )
    """The connection category was not specified (do not use)."""

    OTHER = 1
    """A generic connection for metrics that do not fit into any other category."""

    BATTERY = 2
    """A connection to a metric representing a battery."""

    PV = 3
    """A connection to a metric representing a PV (photovoltaic) array or string."""

    AMBIENT = 10
    """A connection to a metric representing ambient conditions."""

    CABINET = 11
    """A connection to a metric representing a cabinet or an enclosure."""

    HEATSINK = 12
    """A connection to a metric representing a heatsink."""

    TRANSFORMER = 13
    """A connection to a metric representing a transformer."""


@dataclass(frozen=True, kw_only=True)
class MetricConnection:
    """A connection from which a metric was obtained."""

    category: MetricConnectionCategory | int
    """The category of the connection from which the metric was obtained.

    This is the lower-level, forward-compatible accessor: it may hold a known
    `MetricConnectionCategory` member, the raw `int` `0` when the category is
    unspecified, or any other raw `int` not yet known to this client. Prefer
    `MetricConnection.get_category()` to obtain a known member or a clear error.
    """

    name: str = ""
    """The name of the specific connection from which the metric was obtained.

    This is expected to be populated when the same [`Metric`][...Metric] variant
    can be obtained from multiple distinct inputs or connection points on the
    component. Knowing the connection for the metric can help in certain control
    and monitoring applications.
    """

    def __str__(self) -> str:
        """Return a string representation of this connection."""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            match self.category:
                case 0 | MetricConnectionCategory.UNSPECIFIED:
                    category_name = "cat=<invalid:0>"
                case MetricConnectionCategory() as category:
                    category_name = category.name
                case int() as category:
                    category_name = f"cat={category}"
                case unexpected:
                    assert_never(unexpected)
        return f"{self.name}:{category_name}"

    def get_category(self) -> MetricConnectionCategory:
        """Return the connection category as a known enum member.

        This is the higher-level accessor for the lower-level
        [`category`][frequenz.client.common.metrics.MetricConnection.category]
        field: it returns a known member or raises instead of exposing the raw
        sentinel `0` or an unknown `int`.

        Returns:
            The category when it is a known `MetricConnectionCategory` member.

        Raises:
            UnspecifiedEnumValueError: If the category is unspecified (the raw
                value `0` or a member whose value is `0`).
            UnrecognizedEnumValueError: If the category is an `int` this
                client does not recognize. The raw value is available on the
                error's `value` attribute.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            match self.category:
                case 0 | MetricConnectionCategory.UNSPECIFIED:
                    raise UnspecifiedEnumValueError(self, "category")
                case MetricConnectionCategory():
                    return self.category
                case int():
                    raise UnrecognizedEnumValueError(self, "category", self.category)
                case unexpected:
                    assert_never(unexpected)


@dataclass(frozen=True, init=False)
class MetricSample:
    """A sampled metric.

    This represents a single sample of a specific metric, the value of which is either
    measured or derived at a particular time. The real-time system-defined bounds are
    optional and may not always be present or set.

    Note: Relationship Between Bounds and Metric Samples
        Suppose a metric sample for active power has a lower-bound of -10,000 W, and an
        upper-bound of 10,000 W. For the system to accept a charge command, clients need
        to request current values within the bounds.
    """

    sample_time2: datetime | InvalidDatetime
    """The moment when the metric was sampled.

    A [`datetime`][datetime.datetime] for a well-formed wire timestamp, or an
    [`InvalidDatetime`][....InvalidDatetime] preserving the raw seconds and
    nanoseconds when the wire carried a malformed one.

    Tip:
        Prefer [`get_sample_time()`][..get_sample_time] to obtain a valid
        [`datetime`][datetime.datetime] or a clear error.

    Note:
        This field replaces the deprecated [`sample_time`][..sample_time]
        property, which cannot express the malformed case. It will be renamed
        back to `sample_time` once that property is removed.
    """

    metric: Metric | int
    """The metric that was sampled.

    This is the lower-level, forward-compatible accessor: it may hold a known
    `Metric` member, the raw `int` `0` when the metric is unspecified, or any
    other raw `int` not yet known to this client. Prefer
    `MetricSample.get_metric()` to obtain a known member or a clear error.
    """

    value: FloatInt | AggregatedMetricValue | None
    """The value of the sampled metric."""

    bounds_set: BoundsSet | InvalidBoundsSet
    """The bounds that apply to the metric sample.

    These bounds adapt in real-time to reflect the operating conditions at the time of
    aggregation or derivation. They form a union: the value of the metric must be within
    at least one of them, and an empty [`BoundsSet`][...BoundsSet] means the metric is
    unbounded.

    This is a [`BoundsSet`][...BoundsSet] for well-formed data, or an
    [`InvalidBoundsSet`][...InvalidBoundsSet] preserving the raw bounds when the wire
    carried any malformed entry, so callers must handle both.

    Tip:
        Prefer `MetricSample.get_bounds_set()` to obtain a valid `BoundsSet` or a
        clear error.

    In accordance with the passive sign convention, bounds that limit discharge would
    have negative numbers, while those limiting charge, such as for the State of Power
    (SoP) metric, would be positive. Hence bounds can have positive and negative values
    depending on the metric they represent.
    """

    connection: MetricConnection | None = None
    """The specific source or connection from which the metric was sampled.

    This will be present when the same [`Metric`][...Metric] can be obtained from
    multiple sources or connections. Knowing the connection can help in certain
    control and monitoring applications.

    In cases where the component has just one connection for a metric, then the
    connection is `None`.

    Example:
        A hybrid inverter can have a DC string for a battery and another DC string for a
        PV array. The connection names could resemble, say, `dc_battery_0` (category
        `BATTERY`) and `dc_pv_0` (category `PV`). A metric like DC voltage can be
        obtained from both connections. For an application to determine the SoC of the
        battery using the battery voltage, which connection the voltage metric was
        sampled from is important.
    """

    # This custom `__init__` should be removed once the deprecated `bounds` and
    # `sample_time` fields are removed.
    # pylint: disable-next=too-many-arguments
    def __init__(  # noqa: DOC502
        self,
        *,
        sample_time: datetime | None = None,
        sample_time2: datetime | InvalidDatetime | None = None,
        metric: Metric | int,
        value: FloatInt | AggregatedMetricValue | None,
        bounds_set: BoundsSet | InvalidBoundsSet | None = None,
        bounds: list[Bounds] | None = None,
        connection: MetricConnection | None = None,
    ) -> None:
        """Initialize this metric sample.

        Deprecated:
            The `bounds` argument is deprecated since v0.4.1. Use `bounds_set`
            instead.

        Args:
            sample_time: The moment when the metric was sampled, as a
                well-formed [`datetime`][datetime.datetime]. This spelling
                stays valid: it will accept the wider type once
                [`sample_time2`][..sample_time2] is renamed back to
                `sample_time`.
            sample_time2: The moment when the metric was sampled, which may be
                an [`InvalidDatetime`][....InvalidDatetime]. Use this to build
                a sample from a malformed wire timestamp.
            metric: The metric that was sampled.
            value: The value of the sampled metric.
            bounds_set: The bounds that apply to the metric sample.
            bounds: Deprecated alias that accepts a list of valid
                [`Bounds`][...Bounds] and stores them as a
                [`BoundsSet`][...BoundsSet]. Use `bounds_set` instead.
            connection: The source or connection the metric was sampled from.

        Raises:
            TypeError: If both `bounds_set` and the deprecated `bounds` are
                given, or if neither is given; or if both `sample_time` and
                `sample_time2` are given, or if neither is given.
        """
        sample_time2 = self._resolve_sample_time(sample_time, sample_time2)
        bounds_set = self._resolve_bounds_set(bounds_set, bounds)
        object.__setattr__(self, "sample_time2", sample_time2)
        object.__setattr__(self, "metric", metric)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "bounds_set", bounds_set)
        object.__setattr__(self, "connection", connection)

    @staticmethod
    def _resolve_sample_time(
        sample_time: datetime | None, sample_time2: datetime | InvalidDatetime | None
    ) -> datetime | InvalidDatetime:
        """Pick the sample time from the current and the compatibility argument.

        Args:
            sample_time: The compatibility argument.
            sample_time2: The current argument.

        Returns:
            The sample time to store.

        Raises:
            TypeError: If both or neither argument is given.
        """
        if sample_time is not None and sample_time2 is not None:
            raise TypeError(
                "`MetricSample` accepts either `sample_time` or `sample_time2`, "
                "not both."
            )
        if sample_time is not None:
            return sample_time
        if sample_time2 is None:
            raise TypeError("`MetricSample` requires the `sample_time2` argument.")
        return sample_time2

    @staticmethod
    def _resolve_bounds_set(
        bounds_set: BoundsSet | InvalidBoundsSet | None, bounds: list[Bounds] | None
    ) -> BoundsSet | InvalidBoundsSet:
        """Pick the bounds set from the current and the deprecated argument.

        Args:
            bounds_set: The current argument.
            bounds: The deprecated argument.

        Returns:
            The bounds set to store.

        Raises:
            TypeError: If both or neither argument is given.
        """
        if bounds is not None and bounds_set is not None:
            raise TypeError(
                "`MetricSample` accepts either `bounds_set` or the deprecated "
                "`bounds`, not both."
            )
        if bounds is not None:
            warnings.warn(
                "The `bounds` argument is deprecated; use `bounds_set` instead.",
                DeprecationWarning,
                stacklevel=4,
            )
            return BoundsSet(bounds=tuple(bounds))
        if bounds_set is None:
            raise TypeError("`MetricSample` requires the `bounds_set` argument.")
        return bounds_set

    def __str__(self) -> str:
        """Return a compact string representation of this sample."""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            match self.metric:
                case 0 | Metric.UNSPECIFIED:
                    metric = "<invalid:0>"
                case Metric() as known:
                    metric = known.name
                case int() as unknown:
                    metric = str(unknown)
                case unexpected:
                    assert_never(unexpected)
        sample = f"{metric}={self.value}"
        if self.connection is not None:
            sample = f"{sample}@{self.connection}"
        return sample

    @property
    @deprecated(
        "frequenz.client.common.metrics.MetricSample.sample_time is deprecated "
        "since v0.4.1. Use "
        "[frequenz.client.common.metrics.MetricSample.get_sample_time][] instead."
    )
    def sample_time(self) -> datetime:  # noqa: DOC502
        """The moment when the metric was sampled.

        Deprecated:
            This property is deprecated since v0.4.1. Use
            [`get_sample_time()`][..get_sample_time] instead.

        This property keeps the released `datetime` type, so it cannot express
        a malformed wire timestamp and raises for one instead, exactly like
        [`get_sample_time()`][..get_sample_time]. Read
        [`sample_time2`][..sample_time2] to get a malformed timestamp as an
        [`InvalidDatetime`][....InvalidDatetime] instead.

        Returns:
            The sample time, when it is a valid
                [`datetime`][datetime.datetime].

        Raises:
            InvalidDatetimeError: If the sample time is an
                [`InvalidDatetime`][....InvalidDatetime]. The offending
                instance is available on the error's `datetime` attribute.
        """
        return self.get_sample_time()

    @property
    @deprecated(
        "frequenz.client.common.metrics.MetricSample.bounds is deprecated "
        "since v0.4.1. Use "
        "[frequenz.client.common.metrics.MetricSample.bounds_set][] instead."
    )
    def bounds(self) -> list[Bounds]:
        """The valid bounds that apply to the metric sample.

        Deprecated:
            This property is deprecated since v0.4.1. Use
            [`bounds_set`][..bounds_set] instead.

        For backward compatibility this returns only the valid
        [`Bounds`][...Bounds] from `bounds_set` (dropping any malformed entries,
        as the old field did), but it returns the normalized, merged bounds
        rather than the raw list received on the wire.

        Returns:
            The valid bounds in `bounds_set`.
        """
        valid = tuple(
            bound for bound in self.bounds_set.bounds if isinstance(bound, Bounds)
        )
        return list(BoundsSet(bounds=valid).bounds)

    def as_single_value(
        self, *, aggregation_method: AggregationMethod = AggregationMethod.AVG
    ) -> FloatInt | None:
        """Return the value of this sample as a single value.

        If [`value`][..value] is a number, it is returned as is. If `value`
        is an [`AggregatedMetricValue`][...AggregatedMetricValue], the value is
        aggregated using the provided `aggregation_method`.

        Args:
            aggregation_method: The method to use to aggregate the value when `value`
                is an [`AggregatedMetricValue`][...AggregatedMetricValue].

        Returns:
            The value of the sample as a single value, or `None` if the value is `None`.
        """
        match self.value:
            case float() | int():
                return self.value
            case AggregatedMetricValue():
                match aggregation_method:
                    case AggregationMethod.AVG:
                        return self.value.avg
                    case AggregationMethod.MIN:
                        return self.value.min
                    case AggregationMethod.MAX:
                        return self.value.max
                    case unexpected:
                        assert_never(unexpected)
            case None:
                return None
            case unexpected:
                assert_never(unexpected)

    def get_sample_time(self) -> datetime:
        """Return the sample time as a valid `datetime`.

        This is the higher-level accessor for the lower-level
        [`sample_time2`][frequenz.client.common.metrics.MetricSample.sample_time2]
        field: it returns a valid [`datetime`][datetime.datetime] or raises
        instead of exposing an [`InvalidDatetime`][....InvalidDatetime].

        Returns:
            The sample time when it is a valid [`datetime`][datetime.datetime].

        Raises:
            InvalidDatetimeError: If the sample time is an
                [`InvalidDatetime`][....InvalidDatetime]. The offending
                instance is available on the error's `datetime` attribute.
        """
        match self.sample_time2:
            case datetime() as sample_time:
                return sample_time
            case InvalidDatetime() as invalid:
                raise InvalidDatetimeError(self, "sample_time2", invalid)
            case unexpected:
                assert_never(unexpected)

    def get_metric(self) -> Metric:
        """Return the sampled metric as a known enum member.

        This is the higher-level accessor for the lower-level
        [`metric`][frequenz.client.common.metrics.MetricSample.metric] field: it
        returns a known member or raises instead of exposing the raw sentinel
        `0` or an unknown `int`.

        Returns:
            The metric when it is a known `Metric` member.

        Raises:
            UnspecifiedEnumValueError: If the metric is unspecified (the raw
                value `0` or a member whose value is `0`).
            UnrecognizedEnumValueError: If the metric is an `int` this client
                does not recognize. The raw value is available on the error's
                `value` attribute.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            match self.metric:
                case 0 | Metric.UNSPECIFIED:
                    raise UnspecifiedEnumValueError(self, "metric")
                case Metric():
                    return self.metric
                case int():
                    raise UnrecognizedEnumValueError(self, "metric", self.metric)
                case unexpected:
                    assert_never(unexpected)

    def get_bounds_set(self) -> BoundsSet:
        """Return the bounds as a valid `BoundsSet`.

        This is the higher-level accessor for the lower-level
        [`bounds_set`][frequenz.client.common.metrics.MetricSample.bounds_set]
        field: it returns a valid `BoundsSet` or raises instead of exposing an
        `InvalidBoundsSet`.

        Returns:
            The bounds set when it is a valid `BoundsSet`.

        Raises:
            InvalidBoundsSetError: If the bounds set is an `InvalidBoundsSet`.
                The offending set is available on the error's `bounds_set`
                attribute.
        """
        match self.bounds_set:
            case BoundsSet() as bounds_set:
                return bounds_set
            case InvalidBoundsSet() as invalid:
                raise InvalidBoundsSetError(self, "bounds_set", invalid)
            case unexpected:
                assert_never(unexpected)
