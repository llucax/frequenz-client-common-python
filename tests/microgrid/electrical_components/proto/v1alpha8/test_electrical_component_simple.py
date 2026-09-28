# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of simple electrical components."""

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.core.warnings import ignoring_deprecations

from frequenz.client.common.microgrid.electrical_components import (
    Breaker,
    CapacitorBank,
    CategorySpecificInfo,
    Chp,
    Converter,
    CryptoMiner,
    ElectricalComponent,
    ElectricalComponentCategory,
    Electrolyzer,
    GridConnectionPoint,
    Hvac,
    Meter,
    MismatchedCategoryElectricalComponent,
    Plc,
    PowerTransformer,
    Precharger,
    StaticTransferSwitch,
    SteamBoiler,
    UninterruptiblePowerSupply,
    UnrecognizedElectricalComponent,
    UnspecifiedElectricalComponent,
    WindTurbine,
)
from frequenz.client.common.microgrid.electrical_components.proto.v1alpha8 import (
    electrical_component_class_to_proto,
    electrical_component_from_proto,
)
from frequenz.client.common.microgrid.electrical_components.proto.v1alpha8._electrical_component import (  # noqa: E501
    _ElectricalComponentBaseData,
)

from .conftest import assert_base_data, base_data_as_proto


def test_unspecified(default_component_base_data: _ElectricalComponentBaseData) -> None:
    """Test ElectricalComponent with unspecified category."""
    proto = base_data_as_proto(default_component_base_data)

    component = electrical_component_from_proto(proto)

    assert isinstance(component, UnspecifiedElectricalComponent)
    assert_base_data(default_component_base_data, component)
    assert electrical_component_class_to_proto(component) == (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED,
        None,
    )


def test_unrecognized(
    default_component_base_data: _ElectricalComponentBaseData,
) -> None:
    """Test ElectricalComponent with unrecognized category."""
    base_data = default_component_base_data._replace(category=999)
    proto = base_data_as_proto(base_data)

    component = electrical_component_from_proto(proto)

    assert isinstance(component, UnrecognizedElectricalComponent)
    assert_base_data(base_data, component)
    assert electrical_component_class_to_proto(component) == (999, None)


def test_category_mismatch(
    default_component_base_data: _ElectricalComponentBaseData,
) -> None:
    """Test mismatched category handling for category GRID and battery info."""
    base_data = default_component_base_data._replace(
        category=1,  # GRID_CONNECTION_POINT
        category_specific_info=CategorySpecificInfo(
            kind="battery", fields={"type": "BATTERY_TYPE_LI_ION"}
        ),
        category_mismatched=True,
    )
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.battery.type = (
        electrical_components_pb2.BATTERY_TYPE_LI_ION
    )

    component = electrical_component_from_proto(proto)

    assert isinstance(component, MismatchedCategoryElectricalComponent)
    assert_base_data(base_data, component)
    assert component.category_specific_info == CategorySpecificInfo(
        kind="battery", fields={"type": "BATTERY_TYPE_LI_ION"}
    )
    assert component.category_name == "GRID_CONNECTION_POINT"
    assert electrical_component_class_to_proto(component) == (1, None)


with ignoring_deprecations():
    _TRIVIAL_CASES = [
        pytest.param(ElectricalComponentCategory.BREAKER, Breaker, id="Breaker"),
        pytest.param(
            ElectricalComponentCategory.CAPACITOR_BANK,
            CapacitorBank,
            id="CapacitorBank",
        ),
        pytest.param(ElectricalComponentCategory.CHP, Chp, id="Chp"),
        pytest.param(ElectricalComponentCategory.CONVERTER, Converter, id="Converter"),
        pytest.param(
            ElectricalComponentCategory.CRYPTO_MINER, CryptoMiner, id="CryptoMiner"
        ),
        pytest.param(
            ElectricalComponentCategory.ELECTROLYZER, Electrolyzer, id="Electrolyzer"
        ),
        pytest.param(ElectricalComponentCategory.HVAC, Hvac, id="Hvac"),
        pytest.param(ElectricalComponentCategory.METER, Meter, id="Meter"),
        pytest.param(ElectricalComponentCategory.PLC, Plc, id="Plc"),
        pytest.param(
            ElectricalComponentCategory.PRECHARGER, Precharger, id="Precharger"
        ),
        pytest.param(
            ElectricalComponentCategory.STATIC_TRANSFER_SWITCH,
            StaticTransferSwitch,
            id="StaticTransferSwitch",
        ),
        pytest.param(
            ElectricalComponentCategory.STEAM_BOILER, SteamBoiler, id="SteamBoiler"
        ),
        pytest.param(
            ElectricalComponentCategory.UNINTERRUPTIBLE_POWER_SUPPLY,
            UninterruptiblePowerSupply,
            id="UninterruptiblePowerSupply",
        ),
        pytest.param(
            ElectricalComponentCategory.WIND_TURBINE, WindTurbine, id="WindTurbine"
        ),
    ]


@pytest.mark.parametrize("category,component_class", _TRIVIAL_CASES)
def test_trivial(
    category: ElectricalComponentCategory,
    component_class: type[ElectricalComponent],
    default_component_base_data: _ElectricalComponentBaseData,
) -> None:
    """Test component types that don't need special handling."""
    base_data = default_component_base_data._replace(category=category)
    proto = base_data_as_proto(base_data)

    component = electrical_component_from_proto(proto)

    assert isinstance(component, component_class)
    assert not isinstance(component, UnrecognizedElectricalComponent)
    assert_base_data(base_data, component)


@pytest.mark.parametrize("primary", [None, -10.0, 0.0, 230.0])
@pytest.mark.parametrize("secondary", [None, -34.5, 0.0, 400.0])
def test_power_transformer(
    default_component_base_data: _ElectricalComponentBaseData,
    primary: float | None,
    secondary: float | None,
) -> None:
    """Test PowerTransformer component."""
    with ignoring_deprecations():
        category = ElectricalComponentCategory.POWER_TRANSFORMER
    base_data = default_component_base_data._replace(category=category)

    proto = base_data_as_proto(base_data)
    if primary is not None:
        proto.category_specific_info.power_transformer.primary = primary
    if secondary is not None:
        proto.category_specific_info.power_transformer.secondary = secondary

    component = electrical_component_from_proto(proto)

    assert isinstance(component, PowerTransformer)
    assert_base_data(base_data, component)
    assert component.primary_voltage == (
        pytest.approx(primary if primary is not None else 0.0)
    )
    assert component.secondary_voltage == (
        pytest.approx(secondary if secondary is not None else 0.0)
    )


@pytest.mark.parametrize("rated_fuse_current", [None, 0, 23])
def test_grid(
    default_component_base_data: _ElectricalComponentBaseData,
    rated_fuse_current: int | None,
) -> None:
    """Test GridConnectionPoint component with default values."""
    with ignoring_deprecations():
        category = ElectricalComponentCategory.GRID_CONNECTION_POINT
    base_data = default_component_base_data._replace(category=category)

    proto = base_data_as_proto(base_data)
    if rated_fuse_current is not None:
        proto.category_specific_info.grid_connection_point.rated_fuse_current = (
            rated_fuse_current
        )

    component = electrical_component_from_proto(proto)

    assert isinstance(component, GridConnectionPoint)
    assert_base_data(base_data, component)
    assert component.rated_fuse_current == (
        rated_fuse_current if rated_fuse_current is not None else 0
    )
    if rated_fuse_current is None:
        assert component.category_specific_info is None
    else:
        assert component.category_specific_info == CategorySpecificInfo(
            kind="grid_connection_point", fields={}
        )
