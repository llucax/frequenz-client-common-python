# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Fixtures and utilities for testing electrical component protobuf conversion."""

from datetime import datetime, timezone

import pytest
from frequenz.api.common.v1alpha8.metrics import bounds_pb2, metrics_pb2
from frequenz.api.common.v1alpha8.microgrid import lifetime_pb2
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.core.warnings import ignoring_deprecations
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.common.metrics import Bounds, BoundsSet, Metric
from frequenz.client.common.microgrid import Lifetime, MicrogridId
from frequenz.client.common.microgrid.electrical_components import (
    ElectricalComponent,
    ElectricalComponentCategory,
    ElectricalComponentId,
)
from frequenz.client.common.microgrid.electrical_components.proto.v1alpha8._electrical_component import (  # noqa: E501
    _ElectricalComponentBaseData,
)
from frequenz.client.common.proto import datetime_to_proto

DEFAULT_LIFETIME = Lifetime(
    start_time=datetime(2020, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2030, 1, 1, tzinfo=timezone.utc),
)
DEFAULT_COMPONENT_ID = ElectricalComponentId(42)
DEFAULT_MICROGRID_ID = MicrogridId(1)
DEFAULT_NAME = "test_component"
DEFAULT_MODEL = "test_manufacturer test_model"


@pytest.fixture
def component_id() -> ElectricalComponentId:
    """Provide a test component ID."""
    return DEFAULT_COMPONENT_ID


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return DEFAULT_MICROGRID_ID


@pytest.fixture
def default_component_base_data(
    component_id: ElectricalComponentId, microgrid_id: MicrogridId
) -> _ElectricalComponentBaseData:
    """Provide a fixture for common component fields."""
    with ignoring_deprecations():
        category = ElectricalComponentCategory.UNSPECIFIED
    return _ElectricalComponentBaseData(
        component_id=component_id,
        microgrid_id=microgrid_id,
        name=DEFAULT_NAME,
        model=DEFAULT_MODEL,
        category=category,
        lifetime=DEFAULT_LIFETIME,
        metric_config_bounds={
            Metric.AC_ENERGY_ACTIVE: BoundsSet(bounds=(Bounds(lower=0, upper=100),))
        },
        category_specific_info=None,
        provides_telemetry=True,
        accepts_control=True,
        category_mismatched=False,
    )


def assert_base_data(
    base_data: _ElectricalComponentBaseData, other: ElectricalComponent
) -> None:
    """Assert this _ElectricalComponentBaseData equals an ElectricalComponent."""
    assert base_data.component_id == other.id
    assert base_data.microgrid_id == other.microgrid_id
    assert base_data.name == other.name
    assert base_data.model == other.model
    assert base_data.lifetime == other.operational_lifetime
    # pylint: disable=protected-access
    assert base_data.provides_telemetry == other._provides_telemetry
    assert base_data.accepts_control == other._accepts_control
    # pylint: enable=protected-access
    assert base_data.metric_config_bounds == other.metric_config_bounds


_OPERATIONAL_MODE_BY_BOOLS: dict[
    tuple[bool, bool],
    electrical_components_pb2.ElectricalComponentOperationalMode.ValueType,
] = {
    (False, False): (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_INACTIVE
    ),
    (True, False): (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_TELEMETRY_ONLY
    ),
    (False, True): (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_CONTROL_ONLY
    ),
    (True, True): (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_CONTROL_AND_TELEMETRY
    ),
}


def base_data_as_proto(
    base_data: _ElectricalComponentBaseData,
) -> electrical_components_pb2.ElectricalComponent:
    """Convert this _ElectricalComponentBaseData to a protobuf ElectricalComponent.

    Note: only base data with recognized `bool` values for both
    `provides_telemetry` and `accepts_control` can be round-tripped through
    this helper. Tests that need to exercise the unspecified or unrecognized
    cases must build the protobuf message directly.
    """
    provides_telemetry = base_data.provides_telemetry
    accepts_control = base_data.accepts_control
    assert isinstance(provides_telemetry, bool), (
        "base_data_as_proto only supports bool provides_telemetry; "
        f"got {provides_telemetry!r}"
    )
    assert isinstance(accepts_control, bool), (
        "base_data_as_proto only supports bool accepts_control; "
        f"got {accepts_control!r}"
    )
    proto = electrical_components_pb2.ElectricalComponent(
        id=int(base_data.component_id),
        microgrid_id=int(base_data.microgrid_id),
        name=base_data.name,
        model=base_data.model or "",
        category=electrical_components_pb2.ElectricalComponentCategory.ValueType(
            base_data.category
            if isinstance(base_data.category, int)
            else int(base_data.category.value)
        ),
        operational_mode=_OPERATIONAL_MODE_BY_BOOLS[
            (provides_telemetry, accepts_control)
        ],
    )
    # This builder only ever receives valid lifetimes; a malformed timestamp has
    # no protobuf spelling to write back.
    if isinstance(base_data.lifetime, Lifetime):
        lifetime_dict: dict[str, Timestamp] = {}
        if base_data.lifetime.start_time is not None:
            lifetime_dict["start_timestamp"] = datetime_to_proto(
                base_data.lifetime.start_time
            )
        if base_data.lifetime.end_time is not None:
            lifetime_dict["end_timestamp"] = datetime_to_proto(
                base_data.lifetime.end_time
            )
        proto.operational_lifetime.CopyFrom(lifetime_pb2.Lifetime(**lifetime_dict))
    if base_data.metric_config_bounds:
        for metric, bounds_set in base_data.metric_config_bounds.items():
            metric_value = metric.value if isinstance(metric, Metric) else metric
            for bounds in bounds_set.bounds:
                bounds_dict: dict[str, float] = {}
                if bounds.lower is not None:
                    bounds_dict["lower"] = bounds.lower
                if bounds.upper is not None:
                    bounds_dict["upper"] = bounds.upper
                proto.metric_config_bounds.append(
                    electrical_components_pb2.MetricConfigBounds(
                        metric=metrics_pb2.Metric.ValueType(metric_value),
                        config_bounds=bounds_pb2.Bounds(**bounds_dict),
                    )
                )
    return proto
