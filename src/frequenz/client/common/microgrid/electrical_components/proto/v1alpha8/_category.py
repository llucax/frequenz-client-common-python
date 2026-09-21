# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of electrical component categories to/from protobuf v1alpha8."""

import warnings

import typing_extensions
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)

from .....proto import enum_from_proto
from ... import ElectricalComponentCategory


@typing_extensions.deprecated(
    "frequenz.client.common.microgrid.electrical_components.proto.v1alpha8."
    "electrical_component_category_from_proto is deprecated since v0.4.1. Use "
    "[frequenz.client.common.microgrid.electrical_components.proto.v1alpha8."
    "electrical_component_class_from_proto][] instead."
)
def electrical_component_category_from_proto(
    message: electrical_components_pb2.ElectricalComponentCategory.ValueType,
) -> ElectricalComponentCategory | int:
    """Convert a protobuf `ElectricalComponentCategory` value to an enum member.

    Args:
        message: The protobuf message to convert.

    Returns:
        The corresponding
            [`ElectricalComponentCategory`][....ElectricalComponentCategory] enum
            member, or the raw [`int`][] if the protobuf value is not recognized.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return enum_from_proto(message, ElectricalComponentCategory)


@typing_extensions.deprecated(
    "frequenz.client.common.microgrid.electrical_components.proto.v1alpha8."
    "electrical_component_category_to_proto is deprecated since v0.4.1. Use "
    "[frequenz.client.common.microgrid.electrical_components.proto.v1alpha8."
    "electrical_component_class_to_proto][] instead."
)
def electrical_component_category_to_proto(
    category: ElectricalComponentCategory,
) -> electrical_components_pb2.ElectricalComponentCategory.ValueType:
    """Convert an `ElectricalComponentCategory` enum member to a protobuf value.

    Args:
        category: The
            [`ElectricalComponentCategory`][....ElectricalComponentCategory] enum
            member to convert.

    Returns:
        The corresponding protobuf `ElectricalComponentCategory` value.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return electrical_components_pb2.ElectricalComponentCategory.ValueType(
            category.value
        )
