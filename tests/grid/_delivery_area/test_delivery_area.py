# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the DeliveryArea class."""

from dataclasses import dataclass

import pytest
from frequenz.core.warnings import asserting_no_deprecations

from frequenz.client.common import (
    UnrecognizedEnumValueError,
    UnspecifiedEnumValueError,
)
from frequenz.client.common.grid import (
    BaseDeliveryArea,
    DeliveryArea,
    EnergyMarketCodeType,
)


@dataclass(frozen=True, kw_only=True)
class _TestCase:
    """Test case for DeliveryArea creation."""

    name: str
    """Description of the test case."""

    code: str | None
    """The code to use for the delivery area."""

    code_type: EnergyMarketCodeType | int
    """The type of code being used."""

    expected_str: str
    """Expected string representation."""


@pytest.mark.parametrize(
    "case",
    [
        _TestCase(
            name="valid_EIC_code",
            code="10Y1001A1001A450",
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_str="10Y1001A1001A450[EUROPE_EIC]",
        ),
        _TestCase(
            name="valid_NERC_code",
            code="PJM",
            code_type=EnergyMarketCodeType.US_NERC,
            expected_str="PJM[US_NERC]",
        ),
        _TestCase(
            name="unknown_code_type_is_valid",
            code="FR",
            code_type=999,
            expected_str="FR[type=999]",
        ),
    ],
    ids=lambda case: case.name,
)
def test_creation_valid(case: _TestCase) -> None:
    """Well-formed DeliveryArea construction succeeds without warnings."""
    with asserting_no_deprecations():
        area = DeliveryArea(code=case.code, code_type=case.code_type)
    assert area.code == case.code
    assert area.code_type == case.code_type
    assert str(area) == case.expected_str


@pytest.mark.parametrize(
    "case",
    [
        _TestCase(
            name="no_code",
            code=None,
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_str="None[EUROPE_EIC]",
        ),
        _TestCase(
            name="empty_code",
            code="",
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_str="[EUROPE_EIC]",
        ),
    ],
    ids=lambda case: case.name,
)
def test_creation_without_code_emits_deprecation_warning(
    case: _TestCase,
) -> None:
    """Constructing DeliveryArea without a `code` emits a DeprecationWarning."""
    with pytest.warns(
        DeprecationWarning, match="Constructing a DeliveryArea without a `code`"
    ):
        area = DeliveryArea(code=case.code, code_type=case.code_type)
    assert area.code == case.code
    assert area.code_type == case.code_type
    assert str(area) == case.expected_str


def test_creation_with_int_zero_code_type_emits_deprecation_warning() -> None:
    """Constructing DeliveryArea with `code_type=0` emits a DeprecationWarning.

    The unspecified `code_type` is documented as invalid in a future release
    (see the class docstring). `DeliveryArea` trusts its inputs and does not
    annotate them in `__str__`; use `InvalidDeliveryArea` to render the
    invalidity marker explicitly.
    """
    with pytest.warns(
        DeprecationWarning,
        match="Constructing a DeliveryArea with `code_type=0`",
    ):
        area = DeliveryArea(code="DE", code_type=0)
    assert area.code == "DE"
    assert area.code_type == 0
    assert str(area) == "DE[type=0]"


def test_creation_with_unspecified_code_type_member_emits_deprecation_warning() -> None:
    """`__post_init__` warns when `code_type` is the UNSPECIFIED member.

    Accessing [`EnergyMarketCodeType.UNSPECIFIED`][...EnergyMarketCodeType] itself
    emits its own `DeprecationWarning`; this test confirms that constructing a
    `DeliveryArea` with a valid `code` and that pre-accessed member also triggers
    the `__post_init__` invariant warning. Consistent with the `int(0)` case
    above, `DeliveryArea` renders the enum name bare — the invalidity marker
    only appears on `InvalidDeliveryArea`.
    """
    with pytest.deprecated_call():
        unspecified = EnergyMarketCodeType.UNSPECIFIED
    with pytest.warns(
        DeprecationWarning,
        match="Constructing a DeliveryArea with `code_type=0`",
    ):
        area = DeliveryArea(code="DE", code_type=unspecified)
    assert area.code == "DE"
    assert area.code_type is unspecified
    assert str(area) == "DE[UNSPECIFIED]"


@pytest.mark.parametrize(
    "case",
    [
        _TestCase(
            name="empty_code",
            code="",
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_str="",
        ),
        _TestCase(
            name="none_code",
            code=None,
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            expected_str="",
        ),
    ],
    ids=lambda case: case.name,
)
def test_creation_raises_on_invalid_code(case: _TestCase) -> None:
    """`_raise_on_invalid=True` raises `ValueError` on empty/`None` code."""
    with asserting_no_deprecations():
        with pytest.raises(ValueError, match="`code` cannot be None or empty"):
            DeliveryArea(
                code=case.code,
                code_type=case.code_type,
                _raise_on_invalid=True,
            )


def test_creation_raises_on_unspecified_int_code_type() -> None:
    """`_raise_on_invalid=True` raises `ValueError` on `code_type=0`."""
    with asserting_no_deprecations():
        with pytest.raises(
            ValueError, match="`code_type` cannot be 0 \\(UNSPECIFIED\\)"
        ):
            DeliveryArea(code="DE", code_type=0, _raise_on_invalid=True)


def test_creation_raises_on_unspecified_member_code_type() -> None:
    """`_raise_on_invalid=True` raises `ValueError` on the UNSPECIFIED member."""
    with pytest.deprecated_call():
        unspecified = EnergyMarketCodeType.UNSPECIFIED
    with asserting_no_deprecations():
        with pytest.raises(
            ValueError, match="`code_type` cannot be 0 \\(UNSPECIFIED\\)"
        ):
            DeliveryArea(code="DE", code_type=unspecified, _raise_on_invalid=True)


def test_creation_does_not_raise_when_valid() -> None:
    """`_raise_on_invalid=True` does not raise on well-formed data."""
    with asserting_no_deprecations():
        area = DeliveryArea(
            code="DE",
            code_type=EnergyMarketCodeType.EUROPE_EIC,
            _raise_on_invalid=True,
        )
    assert area.code == "DE"
    assert area.code_type is EnergyMarketCodeType.EUROPE_EIC


def test_equality() -> None:
    """Test equality of DeliveryArea objects."""
    area1 = DeliveryArea(
        code="10Y1001A1001A450",
        code_type=EnergyMarketCodeType.EUROPE_EIC,
    )
    area2 = DeliveryArea(
        code="10Y1001A1001A450",
        code_type=EnergyMarketCodeType.EUROPE_EIC,
    )
    area3 = DeliveryArea(code="PJM", code_type=EnergyMarketCodeType.US_NERC)

    assert area1 == area2
    assert area1 != area3


def test_hash() -> None:
    """Test that DeliveryArea objects can be used in sets and as dict keys."""
    area1 = DeliveryArea(
        code="10Y1001A1001A450",
        code_type=EnergyMarketCodeType.EUROPE_EIC,
    )
    area2 = DeliveryArea(
        code="10Y1001A1001A450",
        code_type=EnergyMarketCodeType.EUROPE_EIC,
    )
    area3 = DeliveryArea(code="PJM", code_type=EnergyMarketCodeType.US_NERC)

    area_set = {area1, area2, area3}
    assert len(area_set) == 2  # area1 and area2 are equal


@pytest.mark.parametrize(
    "member",
    [EnergyMarketCodeType.EUROPE_EIC, EnergyMarketCodeType.US_NERC],
    ids=lambda member: member.name,
)
def test_get_code_type_returns_known_member(member: EnergyMarketCodeType) -> None:
    """get_code_type() returns a known member unchanged."""
    area = DeliveryArea(code="10Y1001A1001A450", code_type=member)
    assert area.get_code_type() is member


def test_get_code_type_raises_unspecified_for_int_zero() -> None:
    """get_code_type() raises UnspecifiedEnumValueError for a raw int 0 code type."""
    with pytest.deprecated_call():
        area = DeliveryArea(code="TEST", code_type=0)
    with pytest.raises(UnspecifiedEnumValueError):
        area.get_code_type()


def test_get_code_type_raises_unspecified_for_value_zero_member() -> None:
    """get_code_type() raises UnspecifiedEnumValueError for the value-0 member."""
    with pytest.deprecated_call():
        unspecified = EnergyMarketCodeType.UNSPECIFIED
    with pytest.deprecated_call():
        area = DeliveryArea(code="TEST", code_type=unspecified)
    with asserting_no_deprecations():
        with pytest.raises(UnspecifiedEnumValueError):
            area.get_code_type()


def test_get_code_type_raises_unrecognized_for_unknown_int() -> None:
    """get_code_type() raises UnrecognizedEnumValueError carrying the raw value."""
    area = DeliveryArea(code="TEST", code_type=999)
    with pytest.raises(UnrecognizedEnumValueError) as exc_info:
        area.get_code_type()
    assert exc_info.value.value == 999


def test_is_base_delivery_area_subclass() -> None:
    """`DeliveryArea` is a subclass of `BaseDeliveryArea`."""
    assert issubclass(DeliveryArea, BaseDeliveryArea)
