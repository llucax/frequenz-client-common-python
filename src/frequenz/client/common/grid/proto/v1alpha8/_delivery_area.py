# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Conversion of DeliveryArea and EnergyMarketCodeType to/from protobuf v1alpha8."""

import logging
import warnings

from frequenz.api.common.v1alpha8.grid import delivery_area_pb2
from typing_extensions import deprecated

from ....proto import enum_from_proto
from ..._delivery_area import DeliveryArea, EnergyMarketCodeType, InvalidDeliveryArea

_logger = logging.getLogger(__name__)


def energy_market_code_type_from_proto(
    message: delivery_area_pb2.EnergyMarketCodeType.ValueType,
) -> EnergyMarketCodeType | int:
    """Convert a protobuf `EnergyMarketCodeType` value to an enum member.

    Args:
        message: The protobuf message to convert.

    Returns:
        The corresponding [`EnergyMarketCodeType`][....EnergyMarketCodeType] enum
            member, or the raw [`int`][] if the protobuf value is not recognized.
    """
    return enum_from_proto(message, EnergyMarketCodeType)


def energy_market_code_type_to_proto(
    code_type: EnergyMarketCodeType,
) -> delivery_area_pb2.EnergyMarketCodeType.ValueType:
    """Convert a [`EnergyMarketCodeType`][....EnergyMarketCodeType] enum member to a protobuf value.

    Args:
        code_type: The enum member to convert.

    Returns:
        The corresponding protobuf `EnergyMarketCodeType` value.
    """
    return delivery_area_pb2.EnergyMarketCodeType.ValueType(code_type.value)


@deprecated(
    "frequenz.client.common.grid.proto.v1alpha8.delivery_area_from_proto is "
    "deprecated since v0.4.1. Use "
    "[frequenz.client.common.grid.proto.v1alpha8.delivery_area_from_proto2][] "
    "instead."
)
def delivery_area_from_proto(  # noqa: DOC502
    message: delivery_area_pb2.DeliveryArea,
) -> DeliveryArea:
    """Convert a protobuf message to a [`DeliveryArea`][....DeliveryArea] object.

    [`delivery_area_from_proto2`][..delivery_area_from_proto2] distinguishes
    well-formed from malformed data at the type level
    (`DeliveryArea | InvalidDeliveryArea`) rather than silently constructing a
    `DeliveryArea` with invalid content.

    Args:
        message: The protobuf message to convert.

    Returns:
        The corresponding [`DeliveryArea`][....DeliveryArea] object.
    """
    issues: list[str] = []

    code = message.code or None
    if code is None:
        issues.append("code is empty")

    raw_code_type = message.code_type
    code_type: EnergyMarketCodeType | int = (
        raw_code_type
        if raw_code_type == 0
        else energy_market_code_type_from_proto(raw_code_type)
    )
    if raw_code_type == 0:
        issues.append("code_type is unspecified")
    elif isinstance(code_type, int):
        issues.append("code_type is unrecognized")

    if issues:
        _logger.warning(
            "Found issues in delivery area: %s | Protobuf message:\n%s",
            ", ".join(issues),
            message,
        )

    # `DeliveryArea` emits a `DeprecationWarning` when constructed with
    # invalid data. This function is `@deprecated` itself, callers will see the
    # outer notice pointing to `delivery_area_from_proto2`. Suppress the inner
    # warning here so we don't double-warn.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return DeliveryArea(code=code, code_type=code_type)


def delivery_area_from_proto2(
    message: delivery_area_pb2.DeliveryArea,
) -> DeliveryArea | InvalidDeliveryArea:
    """Convert a protobuf message to a delivery area object.

    A well-formed message becomes a [`DeliveryArea`][....DeliveryArea]; a
    message that fails the `DeliveryArea` invariant becomes an
    [`InvalidDeliveryArea`][....InvalidDeliveryArea] carrying the raw wire
    data so callers can inspect or report it.

    Unknown `int` `code_type` values are treated as valid to
    preserve forward compatibility with new protobuf enum values.

    Warning: `code_type` of `0` will be considered invalid in the future
        A `0` value for `code_type` means it is `UNSPECIFIED`, which should not
        be a valid value, but currently this field is not always being set, and
        we normally fall back to a well-known default, so considering it a
        validation failure at the moment is not practical.

    Args:
        message: The protobuf message to convert.

    Returns:
        A [`DeliveryArea`][....DeliveryArea] when the wire data is
            well-formed, an [`InvalidDeliveryArea`][....InvalidDeliveryArea]
            otherwise.
    """
    raw_code_type = message.code_type
    code_type: EnergyMarketCodeType | int = (
        raw_code_type
        if raw_code_type == 0
        else energy_market_code_type_from_proto(raw_code_type)
    )
    try:
        return DeliveryArea(
            code=message.code, code_type=code_type, _raise_on_invalid=True
        )
    except ValueError:
        pass
    return InvalidDeliveryArea(code=message.code, code_type=code_type)
