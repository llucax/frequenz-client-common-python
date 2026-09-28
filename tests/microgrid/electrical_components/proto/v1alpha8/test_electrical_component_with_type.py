# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of components with a type."""

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.core.warnings import ignoring_deprecations

from frequenz.client.common.microgrid.electrical_components import (
    AcEvCharger,
    Battery,
    BatteryInverter,
    DcEvCharger,
    ElectricalComponentCategory,
    EvCharger,
    HybridEvCharger,
    HybridInverter,
    Inverter,
    LiIonBattery,
    NaIonBattery,
    PvInverter,
    UnrecognizedBattery,
    UnrecognizedEvCharger,
    UnrecognizedInverter,
    UnspecifiedBattery,
    UnspecifiedEvCharger,
    UnspecifiedInverter,
)
from frequenz.client.common.microgrid.electrical_components.proto.v1alpha8 import (
    electrical_component_class_to_proto,
    electrical_component_from_proto,
)
from frequenz.client.common.microgrid.electrical_components.proto.v1alpha8._electrical_component import (  # noqa: E501
    _ElectricalComponentBaseData,
)

from .conftest import assert_base_data, base_data_as_proto


@pytest.mark.parametrize(
    "battery_class, pb_battery_type",
    [
        pytest.param(
            LiIonBattery,
            electrical_components_pb2.BATTERY_TYPE_LI_ION,
            id="LI_ION",
        ),
        pytest.param(
            NaIonBattery,
            electrical_components_pb2.BATTERY_TYPE_NA_ION,
            id="NA_ION",
        ),
        pytest.param(
            UnspecifiedBattery,
            electrical_components_pb2.BATTERY_TYPE_UNSPECIFIED,
            id="UNSPECIFIED",
        ),
        pytest.param(
            UnrecognizedBattery,
            999,
            id="UNRECOGNIZED",
        ),
    ],
)
def test_battery(
    default_component_base_data: _ElectricalComponentBaseData,
    battery_class: type[Battery],
    pb_battery_type: int,
) -> None:
    """Test battery component."""
    with ignoring_deprecations():
        category = ElectricalComponentCategory.BATTERY
    base_data = default_component_base_data._replace(category=category)
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.battery.type = pb_battery_type  # type: ignore[assignment]

    component = electrical_component_from_proto(proto)

    assert isinstance(component, Battery)
    assert isinstance(component, battery_class)
    assert_base_data(base_data, component)
    assert electrical_component_class_to_proto(component) == (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
        pb_battery_type,
    )


@pytest.mark.parametrize(
    "ev_charger_class, pb_ev_charger_type",
    [
        pytest.param(
            AcEvCharger,
            electrical_components_pb2.EV_CHARGER_TYPE_AC,
            id="AC",
        ),
        pytest.param(
            DcEvCharger,
            electrical_components_pb2.EV_CHARGER_TYPE_DC,
            id="DC",
        ),
        pytest.param(
            HybridEvCharger,
            electrical_components_pb2.EV_CHARGER_TYPE_HYBRID,
            id="HYBRID",
        ),
        pytest.param(
            UnspecifiedEvCharger,
            electrical_components_pb2.EV_CHARGER_TYPE_UNSPECIFIED,
            id="UNSPECIFIED",
        ),
        pytest.param(
            UnrecognizedEvCharger,
            999,
            id="UNRECOGNIZED",
        ),
    ],
)
def test_ev_charger(
    default_component_base_data: _ElectricalComponentBaseData,
    ev_charger_class: type[EvCharger],
    pb_ev_charger_type: int,
) -> None:
    """Test EV Charger component."""
    with ignoring_deprecations():
        category = ElectricalComponentCategory.EV_CHARGER
    base_data = default_component_base_data._replace(category=category)
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.ev_charger.type = pb_ev_charger_type  # type: ignore[assignment]

    component = electrical_component_from_proto(proto)

    assert isinstance(component, EvCharger)
    assert isinstance(component, ev_charger_class)
    assert_base_data(base_data, component)
    assert electrical_component_class_to_proto(component) == (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
        pb_ev_charger_type,
    )


@pytest.mark.parametrize(
    "inverter_class, pb_inverter_type",
    [
        pytest.param(
            BatteryInverter,
            electrical_components_pb2.INVERTER_TYPE_BATTERY,
            id="BATTERY",
        ),
        pytest.param(
            PvInverter,
            electrical_components_pb2.INVERTER_TYPE_PV,
            id="PV",
        ),
        pytest.param(
            HybridInverter,
            electrical_components_pb2.INVERTER_TYPE_HYBRID,
            id="HYBRID",
        ),
        pytest.param(
            UnspecifiedInverter,
            electrical_components_pb2.INVERTER_TYPE_UNSPECIFIED,
            id="UNSPECIFIED",
        ),
        pytest.param(
            UnrecognizedInverter,
            999,
            id="UNRECOGNIZED",
        ),
    ],
)
def test_inverter(
    default_component_base_data: _ElectricalComponentBaseData,
    inverter_class: type[Inverter],
    pb_inverter_type: int,
) -> None:
    """Test inverter component."""
    with ignoring_deprecations():
        category = ElectricalComponentCategory.INVERTER
    base_data = default_component_base_data._replace(category=category)
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.inverter.type = pb_inverter_type  # type: ignore[assignment]

    component = electrical_component_from_proto(proto)

    assert isinstance(component, Inverter)
    assert isinstance(component, inverter_class)
    assert_base_data(base_data, component)
    assert electrical_component_class_to_proto(component) == (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
        pb_inverter_type,
    )
