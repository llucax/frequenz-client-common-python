# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for DeliveryArea and related to/from protobuf v1alpha8 conversion."""

import warnings
from dataclasses import dataclass

import pytest
from frequenz.api.common.v1alpha8.grid import delivery_area_pb2
from frequenz.core.warnings import asserting_no_deprecations

from frequenz.client.common import UnspecifiedEnumValueError
from frequenz.client.common.grid import (
    DeliveryArea,
    EnergyMarketCodeType,
    InvalidDeliveryArea,
)
from frequenz.client.common.grid.proto.v1alpha8 import (
    delivery_area_from_proto,
    delivery_area_from_proto2,
    energy_market_code_type_from_proto,
    energy_market_code_type_to_proto,
)
from frequenz.client.common.test.enum_parity import EnumParityTest


class TestEnergyMarketCodeTypeParity(EnumParityTest):
    """Parity tests for the `EnergyMarketCodeType` enum."""

    python_enum = EnergyMarketCodeType
    proto_enum = delivery_area_pb2.EnergyMarketCodeType
    name_prefix = "ENERGY_MARKET_CODE_TYPE_"
    from_proto = staticmethod(energy_market_code_type_from_proto)
    to_proto = staticmethod(energy_market_code_type_to_proto)
    deprecated_members = frozenset({"UNSPECIFIED"})


@dataclass(frozen=True, kw_only=True)
class _DeliveryAreaProtoConversionTestCase:
    """Test case for protobuf conversion."""

    name: str
    """Description of the test case."""

    code: str | None
    """The code to set in the protobuf message."""

    code_type: int
    """The code type to set in the protobuf message."""

    expected_code: str | None
    """Expected code in the resulting DeliveryArea."""

    expected_code_type: EnergyMarketCodeType | int
    """Expected code type in the resulting DeliveryArea."""

    expect_warning: bool
    """Whether to expect a warning during conversion."""


@pytest.mark.parametrize(
    "case",
    [
        _DeliveryAreaProtoConversionTestCase(
            name="valid_EIC_code",
            code="10Y1001A1001A450",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            expected_code="10Y1001A1001A450",
            expected_code_type=EnergyMarketCodeType.EUROPE_EIC,
            expect_warning=False,
        ),
        _DeliveryAreaProtoConversionTestCase(
            name="valid_NERC_code",
            code="PJM",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_US_NERC,
            expected_code="PJM",
            expected_code_type=EnergyMarketCodeType.US_NERC,
            expect_warning=False,
        ),
        _DeliveryAreaProtoConversionTestCase(
            name="no_code",
            code=None,
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            expected_code=None,
            expected_code_type=EnergyMarketCodeType.EUROPE_EIC,
            expect_warning=True,
        ),
        _DeliveryAreaProtoConversionTestCase(
            name="unspecified_code_type",
            code="TEST",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_UNSPECIFIED,
            expected_code="TEST",
            expected_code_type=0,
            expect_warning=True,
        ),
        _DeliveryAreaProtoConversionTestCase(
            name="unknown_code_type",
            code="TEST",
            code_type=999,
            expected_code="TEST",
            expected_code_type=999,
            expect_warning=True,
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto(
    caplog: pytest.LogCaptureFixture, case: _DeliveryAreaProtoConversionTestCase
) -> None:
    """Test conversion from protobuf message to DeliveryArea."""
    # We do the type-ignore here because we want to test the case of an
    # arbitrary int too.
    proto = delivery_area_pb2.DeliveryArea(
        code=case.code or "", code_type=case.code_type  # type: ignore[arg-type]
    )
    with caplog.at_level("WARNING"):
        with pytest.deprecated_call(match="delivery_area_from_proto"):
            area = delivery_area_from_proto(proto)

    assert area.code == case.expected_code
    assert area.code_type == case.expected_code_type

    if case.expect_warning:
        assert len(caplog.records) > 0
        assert "Found issues in delivery area" in caplog.records[0].message
    else:
        assert len(caplog.records) == 0


def test_get_code_type_from_proto_unspecified_raises() -> None:
    """A proto-loaded unspecified code type raises UnspecifiedEnumValueError."""
    proto = delivery_area_pb2.DeliveryArea(
        code="TEST",
        code_type=(
            delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_UNSPECIFIED
        ),
    )
    with pytest.deprecated_call(match="delivery_area_from_proto"):
        area = delivery_area_from_proto(proto)
    assert area.code_type == 0
    with pytest.raises(UnspecifiedEnumValueError):
        area.get_code_type()


def test_from_proto_emits_deprecation_warning() -> None:
    """`delivery_area_from_proto` itself is deprecated and warns on call."""
    proto = delivery_area_pb2.DeliveryArea(
        code="DE",
        code_type=(
            delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC
        ),
    )
    with pytest.deprecated_call(match="delivery_area_from_proto2"):
        delivery_area_from_proto(proto)


def test_from_proto_keeps_warnings_deduplicated() -> None:
    """Silencing its internal deprecation doesn't make warnings show again.

    A `warnings.catch_warnings()` block resets the deduplication history on
    every call (python/cpython#73858), so both warnings would show on every
    iteration instead of once.
    """
    proto = delivery_area_pb2.DeliveryArea(
        code="DE",
        code_type=(
            delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC
        ),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("default")
        for _ in range(3):
            warnings.warn("an unrelated warning", UserWarning)
            delivery_area_from_proto(proto)

    assert [warning.category for warning in caught] == [
        UserWarning,
        DeprecationWarning,
    ]


@dataclass(frozen=True, kw_only=True)
class _FromProto2TestCase:
    """Test case for `delivery_area_from_proto2` conversion."""

    name: str
    """Description of the test case."""

    code: str
    """The code to set in the protobuf message."""

    code_type: int
    """The code type to set in the protobuf message."""

    expected_code: str
    """Expected code in the resulting delivery area."""

    expected_code_type: EnergyMarketCodeType | int
    """Expected code type in the resulting delivery area."""

    expected_type: type
    """Expected concrete type returned by the converter."""


@pytest.mark.parametrize(
    "case",
    [
        _FromProto2TestCase(
            name="valid_EIC_code",
            code="10Y1001A1001A450",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            expected_code="10Y1001A1001A450",
            expected_code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_type=DeliveryArea,
        ),
        _FromProto2TestCase(
            name="valid_NERC_code",
            code="PJM",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_US_NERC,
            expected_code="PJM",
            expected_code_type=EnergyMarketCodeType.US_NERC,
            expected_type=DeliveryArea,
        ),
        _FromProto2TestCase(
            name="unknown_code_type_is_valid",
            code="FR",
            code_type=999,
            expected_code="FR",
            expected_code_type=999,
            expected_type=DeliveryArea,
        ),
        _FromProto2TestCase(
            name="no_code_is_invalid",
            code="",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            expected_code="",
            expected_code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_type=InvalidDeliveryArea,
        ),
        _FromProto2TestCase(
            name="unspecified_code_type_is_invalid",
            code="DE",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_UNSPECIFIED,
            expected_code="DE",
            expected_code_type=0,
            expected_type=InvalidDeliveryArea,
        ),
        _FromProto2TestCase(
            name="no_code_with_unspecified_code_type_is_invalid",
            code="",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_UNSPECIFIED,
            expected_code="",
            expected_code_type=0,
            expected_type=InvalidDeliveryArea,
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto2(
    caplog: pytest.LogCaptureFixture, case: _FromProto2TestCase
) -> None:
    """`delivery_area_from_proto2` returns a `DeliveryArea` or `InvalidDeliveryArea`."""
    proto = delivery_area_pb2.DeliveryArea(
        code=case.code, code_type=case.code_type  # type: ignore[arg-type]
    )
    with caplog.at_level("WARNING"):
        with asserting_no_deprecations():
            area = delivery_area_from_proto2(proto)

    assert isinstance(area, case.expected_type)
    assert area.code == case.expected_code
    assert area.code_type == case.expected_code_type
    # The new converter never logs issues.
    assert len(caplog.records) == 0
