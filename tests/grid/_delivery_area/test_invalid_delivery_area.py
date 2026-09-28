# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the InvalidDeliveryArea class."""

from dataclasses import dataclass

import pytest
from frequenz.core.warnings import asserting_no_deprecations

from frequenz.client.common.grid import (
    BaseDeliveryArea,
    DeliveryArea,
    EnergyMarketCodeType,
    InvalidDeliveryArea,
)


@dataclass(frozen=True, kw_only=True)
class _TestCase:
    """Test case for InvalidDeliveryArea creation."""

    name: str
    """Description of the test case."""

    code: str | None
    """The code to use for the delivery area."""

    code_type: EnergyMarketCodeType | int
    """The type of code being used."""

    expected_str: str
    """Expected string representation."""


def test_is_base_delivery_area_subclass() -> None:
    """`InvalidDeliveryArea` is a subclass of `BaseDeliveryArea`."""
    assert issubclass(InvalidDeliveryArea, BaseDeliveryArea)


@pytest.mark.parametrize(
    "case",
    [
        _TestCase(
            name="empty_code",
            code="",
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_str="<invalid:''>[EUROPE_EIC]",
        ),
        _TestCase(
            name="long_code",
            code="10Y1001A1001A450",
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_str="10Y1001A1001A450[EUROPE_EIC]",
        ),
        _TestCase(
            name="unspecified_code_type_int",
            code="DE",
            code_type=0,
            expected_str="DE[type=<invalid:0>]",
        ),
        _TestCase(
            name="unknown_code_type_int",
            code="DE",
            code_type=999,
            expected_str="DE[type=999]",
        ),
    ],
    ids=lambda case: case.name,
)
def test_creation(case: _TestCase) -> None:
    """`InvalidDeliveryArea` accepts any data with no invariants and no warnings."""
    with asserting_no_deprecations():
        area = InvalidDeliveryArea(code=case.code, code_type=case.code_type)
    assert area.code == case.code
    assert area.code_type == case.code_type
    assert str(area) == case.expected_str


def test_creation_with_none_code_emits_deprecation() -> None:
    """`InvalidDeliveryArea` accepts `None` code but emits a DeprecationWarning."""
    with pytest.warns(
        DeprecationWarning,
        match="Using `None` for `code` is deprecated and will be removed in a future release.",
    ):
        area = InvalidDeliveryArea(code=None, code_type=EnergyMarketCodeType.EUROPE_EIC)
    assert area.code is None
    assert area.code_type == EnergyMarketCodeType.EUROPE_EIC
    assert str(area) == "<invalid:None>[EUROPE_EIC]"


def test_equality() -> None:
    """Two `InvalidDeliveryArea` instances with the same data are equal."""
    area1 = InvalidDeliveryArea(code="", code_type=0)
    area2 = InvalidDeliveryArea(code="", code_type=0)
    area3 = InvalidDeliveryArea(code="X", code_type=0)
    assert area1 == area2
    assert area1 != area3


def test_valid_and_invalid_are_distinct() -> None:
    """A `DeliveryArea` and an `InvalidDeliveryArea` with identical fields are not equal."""
    valid = DeliveryArea(code="DE", code_type=EnergyMarketCodeType.EUROPE_EIC)
    invalid = InvalidDeliveryArea(code="DE", code_type=EnergyMarketCodeType.EUROPE_EIC)
    assert valid != invalid  # type: ignore[comparison-overlap]
