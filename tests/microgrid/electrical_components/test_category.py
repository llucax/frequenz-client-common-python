# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for the deprecation messages of `ElectricalComponentCategory` members."""

import ast
import inspect

import pytest

from frequenz.client.common.microgrid.electrical_components import (
    ElectricalComponentCategory,
    _category,
)

_QUALNAME = "frequenz.client.common.microgrid.electrical_components"

_MEMBER_NAMES = [
    "UNSPECIFIED",
    "GRID_CONNECTION_POINT",
    "METER",
    "INVERTER",
    "CONVERTER",
    "BATTERY",
    "EV_CHARGER",
    "BREAKER",
    "PRECHARGER",
    "CHP",
    "ELECTROLYZER",
    "POWER_TRANSFORMER",
    "HVAC",
    "PLC",
    "CRYPTO_MINER",
    "STATIC_TRANSFER_SWITCH",
    "UNINTERRUPTIBLE_POWER_SUPPLY",
    "CAPACITOR_BANK",
    "WIND_TURBINE",
    "STEAM_BOILER",
]


def _expected_message(name: str) -> str:
    """Build the message each member warns with."""
    return (
        f"{_QUALNAME}.ElectricalComponentCategory.{name} is deprecated. "
        f"Use the {_QUALNAME}.ElectricalComponent class hierarchy "
        f"with isinstance(), or "
        f"{_QUALNAME}.proto.v1alpha8.electrical_component_class_to_proto and "
        f"{_QUALNAME}.proto.v1alpha8.electrical_component_class_from_proto, "
        "instead."
    )


def _class_body() -> list[ast.stmt]:
    """Return the statements of the `ElectricalComponentCategory` class body."""
    tree = ast.parse(inspect.getsource(_category))
    for node in tree.body:
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "ElectricalComponentCategory"
        ):
            return node.body
    raise AssertionError("ElectricalComponentCategory not found")


def _static_members() -> dict[str, tuple[ast.Call, str | None]]:
    """Map each member assigned with `deprecated_member()` to its call and docstring."""
    body = _class_body()
    members: dict[str, tuple[ast.Call, str | None]] = {}
    for index, node in enumerate(body):
        if not (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "deprecated_member"
        ):
            continue
        docstring = None
        if index + 1 < len(body):
            following = body[index + 1]
            if (
                isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
                and isinstance(following.value.value, str)
            ):
                docstring = following.value.value
        members[node.targets[0].id] = (node.value, docstring)
    return members


def test_all_members_deprecated_statically() -> None:
    """Every member must be declared through a static `deprecated_member()` call."""
    assert sorted(_static_members()) == sorted(_MEMBER_NAMES)
    assert sorted(ElectricalComponentCategory.__members__) == sorted(_MEMBER_NAMES)


@pytest.mark.parametrize("name", _MEMBER_NAMES)
def test_member_message_is_literal(name: str) -> None:
    """The message must be a string literal, so the docs can render it."""
    call, _ = _static_members()[name]
    assert len(call.args) == 2
    message = call.args[1]
    assert isinstance(message, ast.Constant)
    assert message.value == _expected_message(name)


@pytest.mark.parametrize("name", _MEMBER_NAMES)
def test_member_docstring_has_a_notice(name: str) -> None:
    """The notice is written by hand, and points at the enum's for the replacement.

    The runtime warning can't be followed like a link, so it explains the
    replacement in full; the notice links the enum, which explains it once.
    """
    _, docstring = _static_members()[name]
    assert docstring is not None
    assert docstring.count("Deprecated:") == 1
    assert "Deprecated since v0.4.1. See" in docstring
    assert "][frequenz.client.common.microgrid.electrical_components." in docstring


@pytest.mark.parametrize("name", _MEMBER_NAMES)
def test_member_runtime_message(name: str) -> None:
    """Accessing a member must warn with exactly the documented message."""
    with pytest.deprecated_call() as record:
        _ = getattr(ElectricalComponentCategory, name)
    messages = [
        str(warning.message)
        for warning in record
        if issubclass(warning.category, DeprecationWarning)
    ]
    assert messages == [_expected_message(name)]
