# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Meta-tests for the `EnumParityTest` scaffold itself.

The enum parity subclasses scattered across ``tests/`` only exercise
`EnumParityTest` against *correctly* mirrored enums, so they never prove that
the scaffold actually fails when parity is broken, nor do they cover the
`absent_members` branch (which has no real-world subclass).

These meta-tests drive `EnumParityTest` directly: each builds a configured
(non-``Test*``, hence not collected) subclass via `_make_parity` and calls its
check methods, asserting both the passing behaviour for well-formed enums and
the failing behaviour for broken ones. Protobuf enums are emulated with
`_FakeProtoEnum` so mismatches can be constructed at will.
"""

from __future__ import annotations

import enum
import warnings
from collections.abc import Callable, Mapping
from types import SimpleNamespace
from typing import Any, cast

import pytest
import typing_extensions
from frequenz.core.enum import Enum as DeprecatingEnum
from frequenz.core.enum import deprecated_member, unique
from frequenz.core.warnings import ignoring_deprecations
from pytest_mock import MockerFixture

from frequenz.client.common.proto import enum_from_proto
from frequenz.client.common.test.enum_parity import EnumParityTest


class _FakeProtoEnum:
    """Minimal stand-in for a generated protobuf enum wrapper.

    Reproduces just the protobuf surface consumed by `EnumParityTest`:
    ``DESCRIPTOR.values``, ``Value(name)``, ``Name(value)`` and
    ``ValueType(value)``. Building one from an explicit name-to-number mapping
    lets the tests construct parity mismatches that real generated enums never
    expose.

    Args:
        names_to_values: Mapping of protobuf value names to their numbers.
    """

    # The capitalized members mirror the generated protobuf API on purpose.
    # pylint: disable=invalid-name

    def __init__(self, names_to_values: Mapping[str, int]) -> None:
        self._names_to_values = dict(names_to_values)
        self._values_to_names = {v: n for n, v in names_to_values.items()}
        self.DESCRIPTOR = SimpleNamespace(
            values=[SimpleNamespace(name=name) for name in names_to_values]
        )

    def Value(self, name: str) -> int:
        """Return the number for a protobuf value name.

        Args:
            name: The protobuf value name.

        Returns:
            The corresponding number.

        Raises:
            ValueError: If the name is unknown (matches protobuf behaviour).
        """
        try:
            return self._names_to_values[name]
        except KeyError as exc:
            raise ValueError(f"Unknown enum value name: {name!r}") from exc

    def Name(self, value: int) -> str:
        """Return the protobuf value name for a number.

        Args:
            value: The protobuf number.

        Returns:
            The corresponding value name.

        Raises:
            ValueError: If the value is unknown (matches protobuf behaviour).
        """
        try:
            return self._values_to_names[value]
        except KeyError as exc:
            raise ValueError(f"Unknown enum value: {value!r}") from exc

    @staticmethod
    def ValueType(value: int) -> int:
        """Coerce a number to the protobuf value type (a plain `int`).

        Args:
            value: The number to coerce.

        Returns:
            The same number as a plain `int`.
        """
        return int(value)


def _value_of(member: enum.Enum) -> int:
    """Return an enum member's numeric value (a stand-in ``*_to_proto``).

    Args:
        member: The enum member to convert.

    Returns:
        The member's numeric value.
    """
    return int(member.value)


# A correctly mirrored enum and its fake protobuf counterpart.
_COLOR_PREFIX = "COLOR_"
_COLOR_PROTO_VALUES = {
    "COLOR_UNSPECIFIED": 0,
    "COLOR_RED": 1,
    "COLOR_GREEN": 2,
    "COLOR_BLUE": 3,
}
_COLOR_PROTO = _FakeProtoEnum(_COLOR_PROTO_VALUES)
_COLOR_PROTO_WITH_NEW_VALUE = _FakeProtoEnum({**_COLOR_PROTO_VALUES, "COLOR_PINK": 4})


@enum.unique
class _Color(enum.Enum):
    """A Python enum correctly mirroring `_COLOR_PROTO`."""

    UNSPECIFIED = 0
    RED = 1
    GREEN = 2
    BLUE = 3


def _color_from_proto(value: int) -> _Color | int:
    """Convert a `_COLOR_PROTO` value to a `_Color` member or raw int.

    Args:
        value: The protobuf enum value.

    Returns:
        The `_Color` member, or the raw `int` for unknown values.
    """
    return enum_from_proto(value, _Color)


def _bogus_from_proto(value: int) -> str:
    """Return a non-int, mimicking a deliberately misbehaving converter.

    Used to prove `EnumParityTest.test_from_proto_unknown` rejects converters
    that fail to return an `int` for unknown values.

    Args:
        value: The protobuf enum value.

    Returns:
        The value rendered as a `str` (intentionally the wrong type).
    """
    return str(value)


# An enum whose ``UNSPECIFIED`` member is deprecated (non-silenced converter).
_DEPRECATED_COLOR_PREFIX = "DC_"
_DEPRECATED_COLOR_PROTO = _FakeProtoEnum(
    {"DC_UNSPECIFIED": 0, "DC_RED": 1, "DC_GREEN": 2}
)


@unique
class _DeprecatedColor(DeprecatingEnum):
    """A Python enum whose `UNSPECIFIED` member is deprecated."""

    UNSPECIFIED = deprecated_member(0, "Use the int 0 instead.")
    RED = 1
    GREEN = 2


def _deprecated_color_from_proto(value: int) -> _DeprecatedColor | int:
    """Convert a `_DEPRECATED_COLOR_PROTO` value to a `_DeprecatedColor`.

    This mirrors a non-silenced converter: resolving the purely-deprecated
    ``UNSPECIFIED`` member via the enum constructor emits a warning.

    Args:
        value: The protobuf enum value.

    Returns:
        The `_DeprecatedColor` member, or the raw `int` for unknown values.
    """
    return enum_from_proto(value, _DeprecatedColor)


# An enum where every member is deprecated, with deprecated converters,
# mirroring the real `EvChargerType` / `BatteryType` configuration.
_GONE_COLOR_PREFIX = "GONE_"
_GONE_COLOR_PROTO = _FakeProtoEnum({"GONE_UNSPECIFIED": 0, "GONE_RED": 1})


@unique
class _GoneColor(DeprecatingEnum):
    """A Python enum where every member is deprecated."""

    UNSPECIFIED = deprecated_member(0, "GONE_UNSPECIFIED is deprecated.")
    RED = deprecated_member(1, "GONE_RED is deprecated.")


@typing_extensions.deprecated("_gone_from_proto is deprecated.")
def _gone_from_proto(value: int) -> _GoneColor | int:
    """Convert a `_GONE_COLOR_PROTO` value to a `_GoneColor` member.

    Mirrors a fully-deprecated converter (`silence_deprecations`): the internal
    member lookup is silenced, but calling the converter still warns.

    Args:
        value: The protobuf enum value.

    Returns:
        The `_GoneColor` member, or the raw `int` for unknown values.
    """
    with ignoring_deprecations():
        return enum_from_proto(value, _GoneColor)


@typing_extensions.deprecated("_gone_to_proto is deprecated.")
def _gone_to_proto(member: _GoneColor) -> int:
    """Convert a `_GoneColor` member to its protobuf number.

    Args:
        member: The `_GoneColor` member.

    Returns:
        The member's numeric value.
    """
    with ignoring_deprecations():
        return int(member.value)


def _make_parity(  # pylint: disable=too-many-arguments
    *,
    python_enum: type[enum.Enum],
    proto_enum: _FakeProtoEnum,
    name_prefix: str,
    from_proto: Callable[..., Any] = _value_of,
    to_proto: Callable[..., int] = _value_of,
    deprecated_members: frozenset[str] = frozenset(),
    absent_members: frozenset[str] = frozenset(),
    silence_deprecations: bool = False,
) -> EnumParityTest:
    """Build a configured `EnumParityTest` instance for direct method calls.

    The created subclass is intentionally *not* named ``Test*`` so `pytest`
    does not collect it; the meta-tests invoke its check methods directly.

    Args:
        python_enum: The Python enum under test.
        proto_enum: The fake protobuf enum under test.
        name_prefix: The protobuf value name prefix.
        from_proto: The ``*_from_proto`` converter.
        to_proto: The ``*_to_proto`` converter.
        deprecated_members: Names expected to be deprecated.
        absent_members: Names expected to be absent from the Python enum.
        silence_deprecations: Whether the converters are themselves deprecated.

    Returns:
        A ready-to-use instance of an `EnumParityTest` subclass.
    """
    namespace: dict[str, Any] = {
        "python_enum": python_enum,
        "proto_enum": proto_enum,
        "name_prefix": name_prefix,
        "from_proto": staticmethod(from_proto),
        "to_proto": staticmethod(to_proto),
        "deprecated_members": deprecated_members,
        "absent_members": absent_members,
        "silence_deprecations": silence_deprecations,
    }
    parity_subclass = type("_ConfiguredParity", (EnumParityTest,), namespace)
    return cast(EnumParityTest, parity_subclass())


def test_correct_enum_passes_all_parity_checks() -> None:
    """A correctly mirrored enum passes every inherited parity check."""
    parity = _make_parity(
        python_enum=_Color,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        from_proto=_color_from_proto,
        to_proto=_value_of,
    )
    for pb_name in _COLOR_PROTO_VALUES:
        parity.test_proto_enum_matches_enum_name(pb_name)
        parity.test_proto_enum_matches_enum_value(pb_name)
        parity.test_from_proto(pb_name)
    for member in _Color:
        parity.test_enum_matches_proto_enum_name(member)
        parity.test_enum_matches_proto_enum_value(member)
        parity.test_to_proto(member)
    parity.test_from_proto_unknown()
    # Both are no-ops here (empty frozensets) and must not raise.
    parity.test_deprecated_members_warn()
    parity.test_absent_members()


def test_proto_value_absent_from_python_is_tolerated() -> None:
    """A protobuf value not yet mirrored in Python is tolerated, not failed."""
    parity = _make_parity(
        python_enum=_Color,
        proto_enum=_COLOR_PROTO_WITH_NEW_VALUE,
        name_prefix=_COLOR_PREFIX,
        from_proto=_color_from_proto,
        to_proto=_value_of,
    )
    # "COLOR_PINK" (4) has no _Color member; the checks must not raise.
    parity.test_proto_enum_matches_enum_name("COLOR_PINK")
    parity.test_proto_enum_matches_enum_value("COLOR_PINK")
    # from_proto returns the raw int for the unmirrored value (the else branch).
    parity.test_from_proto("COLOR_PINK")


def test_value_mismatch_is_detected() -> None:
    """The parity checks fail when a Python member value diverges from protobuf."""

    @enum.unique
    class _MismatchedColor(enum.Enum):
        """A Python enum whose ``RED`` value disagrees with the protobuf one."""

        UNSPECIFIED = 0
        RED = 99  # protobuf COLOR_RED is 1
        GREEN = 2
        BLUE = 3

    parity = _make_parity(
        python_enum=_MismatchedColor,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
    )
    with pytest.raises(AssertionError):
        parity.test_proto_enum_matches_enum_name("COLOR_RED")
    with pytest.raises(AssertionError):
        parity.test_proto_enum_matches_enum_value("COLOR_RED")
    with pytest.raises(AssertionError):
        parity.test_enum_matches_proto_enum_value(_MismatchedColor.RED)


def test_name_mismatch_is_detected() -> None:
    """`test_enum_matches_proto_enum_name` fails when the protobuf name differs."""

    @enum.unique
    class _RenamedColor(enum.Enum):
        """A Python enum whose member name has no matching protobuf name."""

        UNSPECIFIED = 0
        CRIMSON = 1  # protobuf calls value 1 "COLOR_RED", not "COLOR_CRIMSON"

    parity = _make_parity(
        python_enum=_RenamedColor,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
    )
    with pytest.raises(AssertionError):
        parity.test_enum_matches_proto_enum_name(_RenamedColor.CRIMSON)


def test_absent_member_passes_when_python_member_removed() -> None:
    """`test_absent_members` passes when a protobuf value has no Python member."""

    @enum.unique
    class _PartialColor(enum.Enum):
        """A Python enum missing the ``BLUE`` member still kept in protobuf."""

        UNSPECIFIED = 0
        RED = 1
        GREEN = 2

    def _partial_color_from_proto(value: int) -> _PartialColor | int:
        """Convert a `_COLOR_PROTO` value to a `_PartialColor` member or raw int.

        Args:
            value: The protobuf enum value.

        Returns:
            The `_PartialColor` member, or the raw `int` for unknown values.
        """
        return enum_from_proto(value, _PartialColor)

    parity = _make_parity(
        python_enum=_PartialColor,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        from_proto=_partial_color_from_proto,
        absent_members=frozenset({"BLUE"}),
    )
    parity.test_proto_enum_matches_enum_name("COLOR_BLUE")
    parity.test_proto_enum_matches_enum_value("COLOR_BLUE")
    parity.test_from_proto("COLOR_BLUE")
    parity.test_absent_members()


def test_absent_member_still_present_is_detected() -> None:
    """`test_absent_members` fails when a supposedly absent member still exists."""
    parity = _make_parity(
        python_enum=_Color,  # still defines BLUE
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        absent_members=frozenset({"BLUE"}),
    )
    with pytest.raises(AssertionError):
        parity.test_absent_members()


def test_deprecated_member_handling() -> None:
    """Deprecated members warn on access yet still satisfy parity checks."""
    parity = _make_parity(
        python_enum=_DeprecatedColor,
        proto_enum=_DEPRECATED_COLOR_PROTO,
        name_prefix=_DEPRECATED_COLOR_PREFIX,
        from_proto=_deprecated_color_from_proto,
        to_proto=_value_of,
        deprecated_members=frozenset({"UNSPECIFIED"}),
    )
    # Accessing the deprecated member warns.
    parity.test_deprecated_members_warn()
    # Parity checks resolve the deprecated member without leaking a warning.
    parity.test_proto_enum_matches_enum_name("DC_UNSPECIFIED")
    parity.test_proto_enum_matches_enum_value("DC_UNSPECIFIED")
    # from_proto on the deprecated value warns and returns the member.
    parity.test_from_proto("DC_UNSPECIFIED")
    # Non-deprecated members behave normally.
    parity.test_from_proto("DC_RED")


def test_deprecated_member_not_actually_deprecated_is_detected() -> None:
    """`test_deprecated_members_warn` fails if a listed member never warns."""
    parity = _make_parity(
        python_enum=_Color,  # a plain enum: nothing is deprecated
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        from_proto=_color_from_proto,
        to_proto=_value_of,
        deprecated_members=frozenset({"RED"}),
    )
    with pytest.raises(pytest.fail.Exception):
        parity.test_deprecated_members_warn()


def test_silence_deprecations_with_deprecated_converters() -> None:
    """A fully-deprecated enum with deprecated converters still passes."""
    parity = _make_parity(
        python_enum=_GoneColor,
        proto_enum=_GONE_COLOR_PROTO,
        name_prefix=_GONE_COLOR_PREFIX,
        from_proto=_gone_from_proto,
        to_proto=_gone_to_proto,
        deprecated_members=frozenset(m.name for m in _GoneColor),
        silence_deprecations=True,
    )
    # Every member is deprecated -> from_proto takes the warning-asserting branch.
    for pb_name in ("GONE_UNSPECIFIED", "GONE_RED"):
        parity.test_from_proto(pb_name)
    # to_proto / unknown go through the silencing context without leaking warnings.
    for member in _GoneColor:
        parity.test_to_proto(member)
    parity.test_from_proto_unknown()
    parity.test_deprecated_members_warn()


def test_from_proto_unknown_rejects_non_int_result() -> None:
    """`test_from_proto_unknown` fails when the converter returns a non-int."""
    parity = _make_parity(
        python_enum=_Color,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        from_proto=_bogus_from_proto,
        to_proto=_value_of,
    )
    with pytest.raises(AssertionError):
        parity.test_from_proto_unknown()


def test_maybe_ignore_deprecation_suppresses_listed_members() -> None:
    """`_maybe_ignore_deprecation` suppresses warnings only for listed members."""
    # pylint: disable=protected-access
    parity = _make_parity(
        python_enum=_Color,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        deprecated_members=frozenset({"RED"}),
    )
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        with parity._maybe_ignore_deprecation("RED"):
            warnings.warn("dep", DeprecationWarning)
    assert recorded == []

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        with parity._maybe_ignore_deprecation("GREEN"):
            warnings.warn("dep", DeprecationWarning)
    assert len(recorded) == 1


def test_maybe_silence_converter_deprecation_respects_flag() -> None:
    """`_maybe_silence_converter_deprecation` suppresses only when enabled."""
    # pylint: disable=protected-access
    silencing = _make_parity(
        python_enum=_Color,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        silence_deprecations=True,
    )
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        with silencing._maybe_silence_converter_deprecation():
            warnings.warn("dep", DeprecationWarning)
    assert recorded == []

    not_silencing = _make_parity(
        python_enum=_Color,
        proto_enum=_COLOR_PROTO,
        name_prefix=_COLOR_PREFIX,
        silence_deprecations=False,
    )
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        with not_silencing._maybe_silence_converter_deprecation():
            warnings.warn("dep", DeprecationWarning)
    assert len(recorded) == 1


def test_pytest_generate_tests_parametrizes_pb_name(mocker: MockerFixture) -> None:
    """`pytest_generate_tests` parametrizes ``pb_name`` with all protobuf names."""
    parity = _make_parity(
        python_enum=_Color, proto_enum=_COLOR_PROTO, name_prefix=_COLOR_PREFIX
    )
    metafunc = mocker.MagicMock()
    metafunc.fixturenames = ["pb_name"]
    parity.pytest_generate_tests(metafunc)
    metafunc.parametrize.assert_called_once_with("pb_name", list(_COLOR_PROTO_VALUES))


def test_pytest_generate_tests_parametrizes_member(mocker: MockerFixture) -> None:
    """`pytest_generate_tests` parametrizes ``member`` with all enum members."""
    parity = _make_parity(
        python_enum=_Color, proto_enum=_COLOR_PROTO, name_prefix=_COLOR_PREFIX
    )
    metafunc = mocker.MagicMock()
    metafunc.fixturenames = ["member"]
    parity.pytest_generate_tests(metafunc)
    metafunc.parametrize.assert_called_once()
    args, kwargs = metafunc.parametrize.call_args
    assert args == ("member", list(_Color))
    # The ids callable maps each member to its name.
    assert [kwargs["ids"](m) for m in _Color] == [m.name for m in _Color]


def test_pytest_generate_tests_ignores_unrelated_fixtures(
    mocker: MockerFixture,
) -> None:
    """`pytest_generate_tests` does nothing when neither fixture is requested."""
    parity = _make_parity(
        python_enum=_Color, proto_enum=_COLOR_PROTO, name_prefix=_COLOR_PREFIX
    )
    metafunc = mocker.MagicMock()
    metafunc.fixturenames = ["something_else"]
    parity.pytest_generate_tests(metafunc)
    metafunc.parametrize.assert_not_called()
