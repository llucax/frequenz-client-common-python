# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for MetricConnection and MetricConnectionCategory classes."""

import warnings

import pytest

from frequenz.client.common import (
    UnrecognizedEnumValueError,
    UnspecifiedEnumValueError,
)
from frequenz.client.common.metrics import MetricConnection, MetricConnectionCategory


@pytest.mark.parametrize(
    "category,name,expected_str",
    [
        pytest.param(
            MetricConnectionCategory.BATTERY,
            "",
            ":BATTERY",
            id="enum_category_empty_name",
        ),
        pytest.param(
            MetricConnectionCategory.PV,
            "dc_pv_0",
            "dc_pv_0:PV",
            id="enum_category_with_name",
        ),
        pytest.param(
            999,
            "",
            ":cat=999",
            id="int_category_empty_name",
        ),
        pytest.param(
            999,
            "unknown_connection",
            "unknown_connection:cat=999",
            id="int_category_with_name",
        ),
        pytest.param(
            0,
            "",
            ":cat=<invalid:0>",
            id="unspecified_int_empty_name",
        ),
        pytest.param(
            0,
            "conn",
            "conn:cat=<invalid:0>",
            id="unspecified_int_with_name",
        ),
    ],
)
def test_str_representation(
    category: MetricConnectionCategory | int,
    name: str,
    expected_str: str,
) -> None:
    """Test string representation of MetricConnection."""
    connection = MetricConnection(category=category, name=name)
    assert str(connection) == expected_str


def test_creation_with_enum_category() -> None:
    """Test MetricConnection creation with enum category."""
    connection = MetricConnection(
        category=MetricConnectionCategory.BATTERY,
        name="dc_battery_0",
    )
    assert connection.category == MetricConnectionCategory.BATTERY
    assert connection.name == "dc_battery_0"


def test_creation_with_int_category() -> None:
    """Test MetricConnection creation with int category (unrecognized)."""
    connection = MetricConnection(
        category=999,
        name="unknown",
    )
    assert connection.category == 999
    assert connection.name == "unknown"


def test_creation_default_name() -> None:
    """Test MetricConnection creation with default name."""
    connection = MetricConnection(category=MetricConnectionCategory.AMBIENT)
    assert connection.category == MetricConnectionCategory.AMBIENT
    assert not connection.name


def test_equality() -> None:
    """Test equality of MetricConnection objects."""
    conn1 = MetricConnection(
        category=MetricConnectionCategory.BATTERY, name="dc_battery_0"
    )
    conn2 = MetricConnection(
        category=MetricConnectionCategory.BATTERY, name="dc_battery_0"
    )
    conn3 = MetricConnection(category=MetricConnectionCategory.PV, name="dc_pv_0")
    assert conn1 == conn2
    assert conn1 != conn3


def test_hash() -> None:
    """Test that MetricConnection objects can be used in sets and as dict keys."""
    conn1 = MetricConnection(
        category=MetricConnectionCategory.BATTERY, name="dc_battery_0"
    )
    conn2 = MetricConnection(
        category=MetricConnectionCategory.BATTERY, name="dc_battery_0"
    )
    conn3 = MetricConnection(category=MetricConnectionCategory.PV, name="dc_pv_0")
    conn_set = {conn1, conn2, conn3}
    assert len(conn_set) == 2  # conn1 and conn2 are equal


def test_get_category_returns_known_member() -> None:
    """get_category returns the category when it is a known member."""
    connection = MetricConnection(category=MetricConnectionCategory.BATTERY)
    assert connection.get_category() is MetricConnectionCategory.BATTERY


def test_get_category_unspecified_int_raises() -> None:
    """get_category raises UnspecifiedEnumValueError for the raw int 0."""
    connection = MetricConnection(category=0)
    with pytest.raises(UnspecifiedEnumValueError):
        connection.get_category()


def test_get_category_unspecified_member_raises() -> None:
    """get_category raises UnspecifiedEnumValueError for the value-0 member."""
    with pytest.deprecated_call():
        connection = MetricConnection(category=MetricConnectionCategory.UNSPECIFIED)
    with pytest.raises(UnspecifiedEnumValueError):
        connection.get_category()


def test_str_keeps_warnings_deduplicated() -> None:
    """Silencing the internal deprecation doesn't make warnings show again.

    A `warnings.catch_warnings()` block resets the deduplication history on
    every call (python/cpython#73858), so the unrelated warning would show on
    every iteration instead of once.
    """
    connection = MetricConnection(category=0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("default")
        for _ in range(3):
            warnings.warn("an unrelated warning", UserWarning)
            assert str(connection) == ":cat=<invalid:0>"

    assert [warning.category for warning in caught] == [UserWarning]


def test_get_category_unrecognized_int_raises() -> None:
    """get_category raises UnrecognizedEnumValueError carrying the raw int value."""
    connection = MetricConnection(category=99999)
    with pytest.raises(UnrecognizedEnumValueError) as exc_info:
        connection.get_category()
    assert exc_info.value.value == 99999
