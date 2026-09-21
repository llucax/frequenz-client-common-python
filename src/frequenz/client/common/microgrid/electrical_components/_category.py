# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Electrical component categories."""

import typing_extensions
from frequenz.core.enum import Enum, deprecated_member, unique

_QUALNAME = "frequenz.client.common.microgrid.electrical_components"

_REPLACEMENT = (
    f"Use the [{_QUALNAME}.ElectricalComponent][] class hierarchy with isinstance(), "
    f"or [{_QUALNAME}.proto.v1alpha8.electrical_component_class_to_proto][] and "
    f"[{_QUALNAME}.proto.v1alpha8.electrical_component_class_from_proto][], instead."
)


def _member_message(name: str) -> str:
    """Build the deprecation message for a specific enum member.

    Args:
        name: The enum member name.

    Returns:
        The full deprecation message for that member.
    """
    return (
        f"{_QUALNAME}.ElectricalComponentCategory.{name} is deprecated since "
        f"v0.4.1. {_REPLACEMENT}"
    )


# The message is spelled out as a literal rather than built from the constants
# above because griffe-warnings-deprecated only renders the admonition when it
# can read the message statically; a module-level name renders nothing.
@typing_extensions.deprecated(
    "frequenz.client.common.microgrid.electrical_components."
    "ElectricalComponentCategory is deprecated since v0.4.1. Use the "
    "[frequenz.client.common.microgrid.electrical_components."
    "ElectricalComponent][] class hierarchy with isinstance(), or "
    "[frequenz.client.common.microgrid.electrical_components.proto.v1alpha8."
    "electrical_component_class_to_proto][] and "
    "[frequenz.client.common.microgrid.electrical_components.proto.v1alpha8."
    "electrical_component_class_from_proto][], instead."
)
@unique
class ElectricalComponentCategory(Enum):
    """Possible types of microgrid electrical component."""

    UNSPECIFIED = deprecated_member(0, _member_message("UNSPECIFIED"))
    """The component category is unspecified. This should not be used.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    GRID_CONNECTION_POINT = deprecated_member(
        1, _member_message("GRID_CONNECTION_POINT")
    )
    """The point where the local microgrid is connected to the grid.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    METER = deprecated_member(2, _member_message("METER"))
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    INVERTER = deprecated_member(3, _member_message("INVERTER"))
    """An inverter that converts DC to AC power and vice versa.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    CONVERTER = deprecated_member(4, _member_message("CONVERTER"))
    """An electricity converter, e.g., a DC-DC converter.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    BATTERY = deprecated_member(5, _member_message("BATTERY"))
    """A battery energy storage system.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    EV_CHARGER = deprecated_member(6, _member_message("EV_CHARGER"))
    """A station for charging electrical vehicles.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    BREAKER = deprecated_member(7, _member_message("BREAKER"))
    """A circuit breaker, providing protection and switching by disconnecting circuits.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    PRECHARGER = deprecated_member(8, _member_message("PRECHARGER"))
    """A precharger, used for preparing electrical circuits for switching on.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    CHP = deprecated_member(9, _member_message("CHP"))
    """A combined heat and power (CHP) plant.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.

    It generates electricity and useful heat from a single energy source.
    """

    ELECTROLYZER = deprecated_member(10, _member_message("ELECTROLYZER"))
    """A device for splitting water into hydrogen and oxygen using electricity.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    POWER_TRANSFORMER = deprecated_member(11, _member_message("POWER_TRANSFORMER"))
    """A transformer, used for changing the voltage of electrical circuits.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    HVAC = deprecated_member(12, _member_message("HVAC"))
    """A heating, ventilation, and air conditioning (HVAC) system.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    PLC = deprecated_member(13, _member_message("PLC"))
    """A programmable logic controller (PLC).

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    CRYPTO_MINER = deprecated_member(14, _member_message("CRYPTO_MINER"))
    """A device for mining cryptocurrencies.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    STATIC_TRANSFER_SWITCH = deprecated_member(
        15, _member_message("STATIC_TRANSFER_SWITCH")
    )
    """A static transfer switch, used for switching between power sources.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    UNINTERRUPTIBLE_POWER_SUPPLY = deprecated_member(
        16, _member_message("UNINTERRUPTIBLE_POWER_SUPPLY")
    )
    """An uninterruptible power supply (UPS), used to provide backup power.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    CAPACITOR_BANK = deprecated_member(17, _member_message("CAPACITOR_BANK"))
    """A capacitor bank, used for power factor correction and reactive power compensation.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    WIND_TURBINE = deprecated_member(18, _member_message("WIND_TURBINE"))
    """A wind turbine, used to generate electricity from wind energy.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """

    STEAM_BOILER = deprecated_member(19, _member_message("STEAM_BOILER"))
    """A steam boiler, used to generate steam for heating or industrial processes.

    Deprecated:
        This member is deprecated since v0.4.1. See
        [`ElectricalComponentCategory`][...ElectricalComponentCategory] for
        what to use instead.
    """
