# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Electrical component diagnostic codes."""

from frequenz.core.enum import Enum, deprecated_member, unique


@unique
class ElectricalComponentDiagnosticCode(Enum):
    """All diagnostics that can occur across electrical component categories."""

    UNSPECIFIED = deprecated_member(
        0,
        "frequenz.client.common.microgrid.electrical_components."
        "ElectricalComponentDiagnosticCode.UNSPECIFIED is deprecated since "
        "v0.4.1. Use the int value 0 instead if you really need to check for "
        "this low-level value.",
    )
    """Default value. No specific error is specified."""

    UNKNOWN = 1
    """The component is reporting an unknown or an undefined error.

    The sender cannot parse the component error to any of the variants below.
    """

    SWITCH_ON_FAULT = 2
    """The component could not be switched on."""

    UNDERVOLTAGE = 3
    """The component is operating under the minimum rated voltage."""

    OVERVOLTAGE = 4
    """The component is operating over the maximum rated voltage."""

    OVERCURRENT = 5
    """The component is drawing more current than the maximum rated value."""

    OVERCURRENT_CHARGING = 6
    """The component's consumption current is over the maximum rated value during charging."""

    OVERCURRENT_DISCHARGING = 7
    """The component's production current is over the maximum rated value during discharging."""

    OVERTEMPERATURE = 8
    """The component is operating over the maximum rated temperature."""

    UNDERTEMPERATURE = 9
    """The component is operating under the minimum rated temperature."""

    HIGH_HUMIDITY = 10
    """The component is exposed to high humidity levels over the maximum rated value."""

    FUSE_ERROR = 11
    """The component's fuse has blown."""

    PRECHARGE_ERROR = 12
    """The component's precharge unit has failed."""

    PLAUSIBILITY_ERROR = 13
    """Plausibility issues within the component, causing its internal sanity checks to fail."""

    FAULT_CURRENT = 14
    """Fault current detected in the component."""

    SHORT_CIRCUIT = 15
    """Short circuit detected in the component."""

    CONFIG_ERROR = 16
    """Configuration error related to the component."""

    ILLEGAL_COMPONENT_STATE_CODE_REQUESTED = 17
    """An illegal state was requested for the component."""

    HARDWARE_INACCESSIBLE = 18
    """The hardware of the component is inaccessible."""

    INTERNAL = 19
    """An internal error within the component."""

    UNAUTHORIZED = 20
    """The component is unauthorized to perform the last requested action."""

    EXCESS_LEAKAGE_CURRENT = 21
    """Excess leakage current detected, over the threshold defined by the manufacturer."""

    LOW_SYSTEM_INSULATION_RESISTANCE = 22
    """The component is inoperable due to the insulation resistance being too low.

    The threshold is defined by the manufacturer or configured by the user.
    """

    GROUND_FAULT = 23
    """Ground fault detected in the component."""

    ARC_FAULT = 24
    """Arc fault detected in the component."""

    FAN_FAULT = 25
    """Fan fault detected in the component."""

    HARDWARE_FAULT = 26
    """Hardware fault detected in the component."""

    PROTECTIVE_SHUTDOWN = 27
    """The component performed a protective shutdown."""

    GRID_OVERVOLTAGE = 30
    """The component is inoperable due to the grid voltage being too high."""

    GRID_UNDERVOLTAGE = 31
    """The component is inoperable due to the grid voltage being too low."""

    GRID_OVERFREQUENCY = 32
    """The component is inoperable due to the grid frequency being too high."""

    GRID_UNDERFREQUENCY = 33
    """The component is inoperable due to the grid frequency being too low."""

    GRID_DISCONNECTED = 34
    """The component is inoperable due to the grid being disconnected.

    This happens despite the AC relay being closed.
    """

    GRID_VOLTAGE_IMBALANCE = 35
    """The component is inoperable due to the grid voltage being imbalanced.

    This happens when the voltage of one or more phases is outside the
    acceptable range.
    """

    GRID_ABNORMAL = 36
    """The component is inoperable due to the grid being in a non-standard configuration."""

    EV_UNEXPECTED_PILOT_FAILURE = 40
    """Unexpected pilot failure in an electric vehicle (EV) component."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION = 41
    """Electric vehicle (EV) cable was abruptly unplugged from the charging station."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_EV = 42
    """Electric vehicle (EV) cable was abruptly unplugged from the vehicle."""

    EV_CHARGING_CABLE_LOCK_FAILED = 43
    """Electric vehicle (EV) cable lock failure."""

    EV_CHARGING_CABLE_INVALID = 44
    """Invalid electric vehicle (EV) cable."""

    EV_CONSUMER_INCOMPATIBLE = 45
    """Incompatible electric vehicle (EV) plug."""

    BATTERY_IMBALANCE = 50
    """Battery system imbalance detected."""

    BATTERY_LOW_SOH = 51
    """Low state of health (SOH) detected in the battery."""

    BATTERY_BLOCK_ERROR = 52
    """Battery block error detected."""

    BATTERY_CONTROLLER_ERROR = 53
    """Battery controller error detected."""

    BATTERY_RELAY_ERROR = 54
    """Battery relay error detected."""

    BATTERY_CALIBRATION_NEEDED = 56
    """Battery calibration is needed."""

    RELAY_CYCLE_LIMIT_REACHED = 60
    """The battery's DC contactor or relays have reached end of life."""

    PV_REVERSAL_POLARITY = 70
    """Reverse polarity condition detected on the photovoltaic (PV) side."""

    PV_UNDERPERFORMANCE = 71
    """The photovoltaic (PV) system is underperforming."""

    PV_FAULT = 72
    """Fault in the photovoltaic (PV) system."""

    PV_REVERSE_CURRENT = 73
    """Reverse current condition detected on the photovoltaic (PV) side."""

    PV_GROUND_FAULT = 74
    """Ground fault detected on the photovoltaic (PV) side."""

    INVERTER_DC_UNDERVOLTAGE = 80
    """The inverter is inoperable due to the DC voltage being too low."""

    INVERTER_DC_OVERVOLTAGE = 81
    """The inverter is inoperable due to the DC voltage being too high."""
