# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for deprecation of the category enum and its proto converters."""

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.core.warnings import asserting_no_deprecations, ignoring_deprecations

from frequenz.client.common.microgrid.electrical_components import (
    ElectricalComponentCategory,
    LiIonBattery,
)
from frequenz.client.common.microgrid.electrical_components.proto.v1alpha8 import (
    electrical_component_category_from_proto,
    electrical_component_category_to_proto,
    electrical_component_class_to_proto,
)


def test_electrical_component_category_member_warns() -> None:
    """Accessing an `ElectricalComponentCategory` member must warn."""
    with pytest.deprecated_call():
        _ = ElectricalComponentCategory.BATTERY


def test_electrical_component_category_to_proto_warns() -> None:
    """Calling `electrical_component_category_to_proto` must warn."""
    with ignoring_deprecations():
        member = ElectricalComponentCategory.BATTERY
    with pytest.deprecated_call():
        _ = electrical_component_category_to_proto(member)


def test_electrical_component_category_from_proto_warns() -> None:
    """Calling `electrical_component_category_from_proto` must warn."""
    with pytest.deprecated_call():
        _ = electrical_component_category_from_proto(
            electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY
        )


def test_class_to_proto_does_not_warn() -> None:
    """The non-deprecated `electrical_component_class_to_proto` must NOT warn."""
    with asserting_no_deprecations():
        result = electrical_component_class_to_proto(LiIonBattery)
    assert result == (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
        electrical_components_pb2.BATTERY_TYPE_LI_ION,
    )
