# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Supported metrics for microgrid components."""

from frequenz.core.enum import Enum, deprecated_member, unique


@unique
class Metric(Enum):
    """List of supported metrics.

    Metric units are as follows:

    * `VOLTAGE`: V (Volts)
    * `CURRENT`: A (Amperes)
    * `POWER_ACTIVE`: W (Watts)
    * `POWER_APPARENT`: VA (Volt-Amperes)
    * `POWER_REACTIVE`: VAr (Volt-Amperes reactive)
    * `ENERGY_ACTIVE`: Wh (Watt-hours)
    * `ENERGY_APPARENT`: VAh (Volt-Ampere hours)
    * `ENERGY_REACTIVE`: VArh (Volt-Ampere reactive hours)
    * `FREQUENCY`: Hz (Hertz)
    * `TEMPERATURE`: °C (Degree Celsius)
    * `BATTERY_SOC_PCT`: % (percentage)
    * `BATTERY_CAPACITY`: Wh (Watt-hours)
    * `FACTOR`: no unit

    Note: AC energy metrics information
        - This energy metric is reported directly from the component, and not a
          result of aggregations in our systems. If a component does not have this
          metric, this field cannot be populated.

        - Components that provide energy metrics reset this metric from time to
          time. This behaviour is specific to each component model. E.g., some
          components reset it on UTC 00:00:00.

        - This energy metric does not specify the start time of the accumulation
          period, and therefore can be inconsistent.
    """

    UNSPECIFIED = deprecated_member(
        0,
        "frequenz.client.common.metrics.Metric.UNSPECIFIED is deprecated since "
        "v0.4.1. Use the int value 0 instead if you really need to check for "
        "this low-level value.",
    )
    """The metric is unspecified (this should not be used)."""

    DC_VOLTAGE = 1
    """The DC voltage."""

    DC_CURRENT = 2
    """The DC current."""

    DC_POWER = 3
    """The DC power."""

    AC_FREQUENCY = 10
    """The AC frequency."""

    AC_VOLTAGE = 11
    """The AC electric potential difference."""

    AC_VOLTAGE_PHASE_1_N = 12
    """The AC electric potential difference between phase 1 and neutral."""

    AC_VOLTAGE_PHASE_2_N = 13
    """The AC electric potential difference between phase 2 and neutral."""

    AC_VOLTAGE_PHASE_3_N = 14
    """The AC electric potential difference between phase 3 and neutral."""

    AC_VOLTAGE_PHASE_1_PHASE_2 = 15
    """The AC electric potential difference between phase 1 and phase 2."""

    AC_VOLTAGE_PHASE_2_PHASE_3 = 16
    """The AC electric potential difference between phase 2 and phase 3."""

    AC_VOLTAGE_PHASE_3_PHASE_1 = 17
    """The AC electric potential difference between phase 3 and phase 1."""

    AC_CURRENT = 18
    """The AC current."""

    AC_CURRENT_PHASE_1 = 19
    """The AC current in phase 1."""

    AC_CURRENT_PHASE_2 = 20
    """The AC current in phase 2."""

    AC_CURRENT_PHASE_3 = 21
    """The AC current in phase 3."""

    AC_POWER_APPARENT = 22
    """The AC apparent power."""

    AC_POWER_APPARENT_PHASE_1 = 23
    """The AC apparent power in phase 1."""

    AC_POWER_APPARENT_PHASE_2 = 24
    """The AC apparent power in phase 2."""

    AC_POWER_APPARENT_PHASE_3 = 25
    """The AC apparent power in phase 3."""

    AC_POWER_ACTIVE = 26
    """The AC active power."""

    AC_POWER_ACTIVE_PHASE_1 = 27
    """The AC active power in phase 1."""

    AC_POWER_ACTIVE_PHASE_2 = 28
    """The AC active power in phase 2."""

    AC_POWER_ACTIVE_PHASE_3 = 29
    """The AC active power in phase 3."""

    AC_POWER_REACTIVE = 30
    """The AC reactive power."""

    AC_POWER_REACTIVE_PHASE_1 = 31
    """The AC reactive power in phase 1."""

    AC_POWER_REACTIVE_PHASE_2 = 32
    """The AC reactive power in phase 2."""

    AC_POWER_REACTIVE_PHASE_3 = 33
    """The AC reactive power in phase 3."""

    AC_POWER_FACTOR = 40
    """The AC power factor."""

    AC_POWER_FACTOR_PHASE_1 = 41
    """The AC power factor in phase 1."""

    AC_POWER_FACTOR_PHASE_2 = 42
    """The AC power factor in phase 2."""

    AC_POWER_FACTOR_PHASE_3 = 43
    """The AC power factor in phase 3."""

    AC_ENERGY_APPARENT = 50
    """The AC apparent energy."""

    AC_ENERGY_APPARENT_PHASE_1 = 51
    """The AC apparent energy in phase 1."""

    AC_ENERGY_APPARENT_PHASE_2 = 52
    """The AC apparent energy in phase 2."""

    AC_ENERGY_APPARENT_PHASE_3 = 53
    """The AC apparent energy in phase 3."""

    AC_ENERGY_ACTIVE = 54
    """The AC active energy."""

    AC_ENERGY_ACTIVE_PHASE_1 = 55
    """The AC active energy in phase 1."""

    AC_ENERGY_ACTIVE_PHASE_2 = 56
    """The AC active energy in phase 2."""

    AC_ENERGY_ACTIVE_PHASE_3 = 57
    """The AC active energy in phase 3."""

    AC_ENERGY_ACTIVE_CONSUMED = 58
    """The AC active energy consumed."""

    AC_ENERGY_ACTIVE_CONSUMED_PHASE_1 = 59
    """The AC active energy consumed in phase 1."""

    AC_ENERGY_ACTIVE_CONSUMED_PHASE_2 = 60
    """The AC active energy consumed in phase 2."""

    AC_ENERGY_ACTIVE_CONSUMED_PHASE_3 = 61
    """The AC active energy consumed in phase 3."""

    AC_ENERGY_ACTIVE_DELIVERED = 62
    """The AC active energy delivered."""

    AC_ENERGY_ACTIVE_DELIVERED_PHASE_1 = 63
    """The AC active energy delivered in phase 1."""

    AC_ENERGY_ACTIVE_DELIVERED_PHASE_2 = 64
    """The AC active energy delivered in phase 2."""

    AC_ENERGY_ACTIVE_DELIVERED_PHASE_3 = 65
    """The AC active energy delivered in phase 3."""

    AC_ENERGY_REACTIVE = 66
    """The AC reactive energy."""

    AC_ENERGY_REACTIVE_PHASE_1 = 67
    """The AC reactive energy in phase 1."""

    AC_ENERGY_REACTIVE_PHASE_2 = 68
    """The AC reactive energy in phase 2."""

    AC_ENERGY_REACTIVE_PHASE_3 = 69
    """The AC reactive energy in phase 3."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT = 80
    """The AC total harmonic distortion current."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_1 = 81
    """The AC total harmonic distortion current in phase 1."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_2 = 82
    """The AC total harmonic distortion current in phase 2."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_3 = 83
    """The AC total harmonic distortion current in phase 3."""

    BATTERY_CAPACITY = 100
    """The capacity of the battery."""

    BATTERY_SOC_PCT = 101
    """The state of charge of the battery as a percentage."""

    BATTERY_TEMPERATURE = 102
    """The temperature of the battery."""

    INVERTER_TEMPERATURE = 120
    """The temperature of the inverter."""

    INVERTER_TEMPERATURE_CABINET = 121
    """The temperature of the inverter cabinet."""

    INVERTER_TEMPERATURE_HEATSINK = 122
    """The temperature of the inverter heatsink."""

    INVERTER_TEMPERATURE_TRANSFORMER = 123
    """The temperature of the inverter transformer."""

    EV_CHARGER_TEMPERATURE = 140
    """The temperature of the EV charger."""

    SENSOR_WIND_SPEED = 160
    """The speed of the wind measured."""

    SENSOR_WIND_DIRECTION = 161
    """The direction of the wind measured."""

    SENSOR_TEMPERATURE = 162
    """The temperature measured."""

    SENSOR_RELATIVE_HUMIDITY = 163
    """The relative humidity measured."""

    SENSOR_DEW_POINT = 164
    """The dew point measured."""

    SENSOR_AIR_PRESSURE = 165
    """The air pressure measured."""

    SENSOR_IRRADIANCE = 166
    """The irradiance measured."""
