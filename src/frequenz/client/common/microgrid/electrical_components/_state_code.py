# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Electrical component state codes."""

from frequenz.core.enum import Enum, deprecated_member, unique


@unique
class ElectricalComponentStateCode(Enum):
    """All possible states of a microgrid electrical component."""

    UNSPECIFIED = deprecated_member(
        0,
        "frequenz.client.common.microgrid.electrical_components."
        "ElectricalComponentStateCode.UNSPECIFIED is deprecated since v0.4.1. "
        "Use the int value 0 instead if you really need to check for this "
        "low-level value.",
    )
    """Default value when the component state is not explicitly set."""

    UNKNOWN = 1
    """The component is in an unknown or undefined condition.

    This is used when the sender is unable to classify the component into any
    other state.
    """

    UNAVAILABLE = 2
    """The component is temporarily unavailable for operation."""

    SWITCHING_OFF = 3
    """The component is in the process of switching off."""

    OFF = 4
    """The component has successfully switched off."""

    SWITCHING_ON = 5
    """The component is in the process of switching on from an off state."""

    STANDBY = 6
    """The component is in standby mode, and not immediately ready for operation."""

    READY = 7
    """The component is fully operational and ready for use."""

    CHARGING = 8
    """The component is actively consuming energy."""

    DISCHARGING = 9
    """The component is actively producing or releasing energy."""

    ERROR = 10
    """The component is in an error state and may need attention."""

    EV_CHARGING_CABLE_UNPLUGGED = 20
    """The Electric Vehicle (EV) charging cable is unplugged from the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_STATION = 21
    """The EV charging cable is plugged into the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_EV = 22
    """The EV charging cable is plugged into the vehicle."""

    EV_CHARGING_CABLE_LOCKED_AT_STATION = 23
    """The EV charging cable is locked at the charging station end, ready for charging."""

    EV_CHARGING_CABLE_LOCKED_AT_EV = 24
    """The EV charging cable is locked at the vehicle end, indicating that charging is active."""

    RELAY_OPEN = 30
    """The relay is in an open state, meaning no current can flow through."""

    RELAY_CLOSED = 31
    """The relay is in a closed state, allowing current to flow."""

    PRECHARGER_OPEN = 40
    """The precharger circuit is open, meaning it's not currently active."""

    PRECHARGER_PRECHARGING = 41
    """The precharger is in a precharging state, preparing the main circuit for activation."""

    PRECHARGER_CLOSED = 42
    """The precharger circuit is closed, allowing full current to flow to the main circuit."""
