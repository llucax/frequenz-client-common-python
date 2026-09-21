# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Electrical component categories."""

import typing_extensions
from frequenz.core.enum import Enum, deprecated_member, unique


# Every deprecation message here is spelled out as a literal rather than built
# from shared constants, as the deprecations guide asks, because
# griffe-frequenz-core only reads messages it can see statically.
@typing_extensions.deprecated(
    "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory is "
    "deprecated. "
    "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
    "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components.proto."
    "v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
    "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead."
)
@unique
class ElectricalComponentCategory(Enum):
    """Possible types of microgrid electrical component.

    Deprecated:
        Deprecated since v0.4.1. Use the
        [`ElectricalComponent`][frequenz.client.common.microgrid.electrical_components.ElectricalComponent]
        class hierarchy with isinstance(), or
        [`frequenz.client.common.microgrid.electrical_components.proto.v1alpha8.electrical_component_class_to_proto`][]
        and
        [`frequenz.client.common.microgrid.electrical_components.proto.v1alpha8.electrical_component_class_from_proto`][],
        instead.
    """

    UNSPECIFIED = deprecated_member(
        0,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "UNSPECIFIED is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """The component category is unspecified. This should not be used.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    GRID_CONNECTION_POINT = deprecated_member(
        1,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "GRID_CONNECTION_POINT is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """The point where the local microgrid is connected to the grid.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    METER = deprecated_member(
        2,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory.METER "
        "is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    INVERTER = deprecated_member(
        3,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "INVERTER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """An inverter that converts DC to AC power and vice versa.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    CONVERTER = deprecated_member(
        4,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "CONVERTER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """An electricity converter, e.g., a DC-DC converter.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    BATTERY = deprecated_member(
        5,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "BATTERY is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A battery energy storage system.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    EV_CHARGER = deprecated_member(
        6,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "EV_CHARGER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A station for charging electrical vehicles.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    BREAKER = deprecated_member(
        7,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "BREAKER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A circuit breaker, providing protection and switching by disconnecting circuits.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    PRECHARGER = deprecated_member(
        8,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "PRECHARGER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A precharger, used for preparing electrical circuits for switching on.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    CHP = deprecated_member(
        9,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory.CHP is "
        "deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A combined heat and power (CHP) plant.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.

    It generates electricity and useful heat from a single energy source.
    """

    ELECTROLYZER = deprecated_member(
        10,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "ELECTROLYZER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A device for splitting water into hydrogen and oxygen using electricity.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    POWER_TRANSFORMER = deprecated_member(
        11,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "POWER_TRANSFORMER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A transformer, used for changing the voltage of electrical circuits.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    HVAC = deprecated_member(
        12,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory.HVAC "
        "is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A heating, ventilation, and air conditioning (HVAC) system.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    PLC = deprecated_member(
        13,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory.PLC is "
        "deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A programmable logic controller (PLC).

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    CRYPTO_MINER = deprecated_member(
        14,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "CRYPTO_MINER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A device for mining cryptocurrencies.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    STATIC_TRANSFER_SWITCH = deprecated_member(
        15,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "STATIC_TRANSFER_SWITCH is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A static transfer switch, used for switching between power sources.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    UNINTERRUPTIBLE_POWER_SUPPLY = deprecated_member(
        16,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "UNINTERRUPTIBLE_POWER_SUPPLY is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """An uninterruptible power supply (UPS), used to provide backup power.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    CAPACITOR_BANK = deprecated_member(
        17,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "CAPACITOR_BANK is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A capacitor bank, used for power factor correction and reactive power compensation.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    WIND_TURBINE = deprecated_member(
        18,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "WIND_TURBINE is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A wind turbine, used to generate electricity from wind energy.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """

    STEAM_BOILER = deprecated_member(
        19,
        "frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory."
        "STEAM_BOILER is deprecated. "
        "Use the frequenz.client.common.microgrid.electrical_components.ElectricalComponent class "
        "hierarchy with isinstance(), or frequenz.client.common.microgrid.electrical_components."
        "proto.v1alpha8.electrical_component_class_to_proto and frequenz.client.common.microgrid."
        "electrical_components.proto.v1alpha8.electrical_component_class_from_proto, instead.",
    )
    """A steam boiler, used to generate steam for heating or industrial processes.

    Deprecated:
        Deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory]
        for what to use instead.
    """
