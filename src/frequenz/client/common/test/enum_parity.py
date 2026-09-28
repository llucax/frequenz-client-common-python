# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Shared parity and conversion test base class for protobuf-backed enums.

Every Python enum that mirrors a protobuf enum follows the same convention:

* The protobuf enum value name is a fixed prefix (e.g. `EVENT_`) followed by
  the Python enum member name.
* The protobuf enum value number matches the Python enum value.
* There is a versioned `<enum>_from_proto` function returning the Python
  enum member for known values and the raw [`int`][] for unknown values.
* There is a versioned `<enum>_to_proto` function returning the numeric
  protobuf value.

[`EnumParityTest`][.EnumParityTest] is a parametrized [`pytest`][pytest]
base class covering all those invariants. New enum wrappers add a one-line
subclass that pins the protobuf-specific attributes instead of copy-pasting
the same scaffold.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterator
from enum import Enum
from typing import Any, ClassVar

import pytest
from frequenz.core.warnings import ignoring_deprecations


class EnumParityTest:
    """Base test class checking protobuf/Python enum parity.

    Subclasses must set [`python_enum`][.python_enum],
    [`proto_enum`][.proto_enum], [`name_prefix`][.name_prefix],
    [`from_proto`][.from_proto] and [`to_proto`][.to_proto]. The subclass
    name must start with `Test` so [`pytest`][pytest] picks it up.

    For each subclass, the inherited tests verify that:

    * every protobuf enum name maps to a Python enum member with the same value
      (tolerating new protobuf values not yet mirrored in Python);
    * every Python enum member maps to a protobuf enum name and value;
    * [`from_proto`][.from_proto] returns the matching member for known values
      and the raw [`int`][] for unknown values;
    * [`to_proto`][.to_proto] returns the numeric protobuf value.

    Info: Deprecation-aware mode
        Subclasses may pin `deprecated_members` and/or `absent_members` to make
        the parity checks aware of enum members that are deprecated or have been
        removed. Both default to an empty `frozenset`, so subclasses that leave
        them unset keep the exact behaviour described above.

        * A name listed in `deprecated_members` is expected to emit a
          `DeprecationWarning` when accessed; the inherited parity checks assert
          that warning and otherwise treat the member like any known value.
        * A name listed in `absent_members` is expected to be missing from the
          Python enum while the protobuf enum still defines it.
        * Set `silence_deprecations` to `True` when the ``from_proto`` /
          ``to_proto`` converters are themselves deprecated (the whole enum is
          being retired). The parity checks then suppress the
          `DeprecationWarning` those converters emit, leaving the member-level
          deprecation checks (`deprecated_members`) untouched.

    Subclasses are free to add further `test_*` methods.

    Example:
        ```python
        from frequenz.api.common.v1alpha8.streaming import event_pb2

        from frequenz.client.common.streaming import Event
        from frequenz.client.common.streaming.proto.v1alpha8 import (
            event_from_proto,
            event_to_proto,
        )

        from frequenz.client.common.test.enum_parity import EnumParityTest


        class TestEventParity(EnumParityTest):
            python_enum = Event
            proto_enum = event_pb2.Event
            name_prefix = "EVENT_"
            from_proto = staticmethod(event_from_proto)
            to_proto = staticmethod(event_to_proto)
        ```
    """

    python_enum: ClassVar[type[Enum]]
    """The Python enum subclass mirroring the protobuf enum."""

    proto_enum: ClassVar[Any]
    """The generated protobuf enum wrapper (e.g. `event_pb2.Event`).

    Must expose `DESCRIPTOR.values`, `Value(name)`, `Name(value)` and
    `ValueType`.
    """

    name_prefix: ClassVar[str]
    """Prefix used for protobuf enum value names (e.g. `"EVENT_"`)."""

    from_proto: ClassVar[Callable[..., Any]]
    """Versioned converter from a protobuf enum value to the Python enum.

    Returns the Python enum member for known values, or the raw [`int`][] for
    unknown values. Bind with `staticmethod(...)` in the subclass.
    """

    to_proto: ClassVar[Callable[..., int]]
    """Versioned converter from a Python enum member to a protobuf enum value.

    Bind with `staticmethod(...)` in the subclass.
    """

    deprecated_members: ClassVar[frozenset[str]] = frozenset()
    """The names of members (without [`name_prefix`][..name_prefix]) expected to be deprecated.

    Accessing them must emit a [`DeprecationWarning`][].
    """

    absent_members: ClassVar[frozenset[str]] = frozenset()
    """The names of members (without [`name_prefix`][..name_prefix]) expected to be absent.

    These members are expected to be absent from the Python enum while still
    defined in the protobuf enum.
    """

    silence_deprecations: ClassVar[bool] = False
    """Whether the [`from_proto`][..from_proto]/[`to_proto`][..to_proto] converters are deprecated.

    When `True`, the parity checks suppress the `DeprecationWarning` emitted by
    calling them (member-level deprecation checks are unaffected).
    """

    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        """Parametrize `pb_name` and `member` from the configured enums.

        Args:
            metafunc: The `pytest` metafunc object for the test being collected.
        """
        if "pb_name" in metafunc.fixturenames:
            pb_names = [m.name for m in self.proto_enum.DESCRIPTOR.values]
            metafunc.parametrize("pb_name", pb_names)
        if "member" in metafunc.fixturenames:
            members = list(self.python_enum)
            metafunc.parametrize("member", members, ids=lambda m: m.name)

    @contextlib.contextmanager
    def _maybe_ignore_deprecation(self, name: str) -> Iterator[None]:
        """Suppress deprecation warnings while accessing a deprecated member.

        Parity checks that merely resolve a member must stay warning-clean; the
        warning itself is asserted by `test_deprecated_members_warn`.

        Args:
            name: The member name (without ``name_prefix``) being accessed.

        Yields:
            Control to the wrapped block, with `DeprecationWarning` suppressed
                when ``name`` is in `deprecated_members`.
        """
        if name in self.deprecated_members:
            with ignoring_deprecations():
                yield
        else:
            yield

    @contextlib.contextmanager
    def _maybe_silence_converter_deprecation(self) -> Iterator[None]:
        """Suppress converter `DeprecationWarning`s when `silence_deprecations` is set.

        Some enums expose `from_proto` / `to_proto` converters that are
        themselves deprecated (the whole enum is being retired). Calling them in
        the parity checks emits a `DeprecationWarning` unrelated to member
        deprecation, which would otherwise fail the warning-clean checks.

        Yields:
            Control to the wrapped block, with `DeprecationWarning` suppressed
                when `silence_deprecations` is `True`.
        """
        if self.silence_deprecations:
            with ignoring_deprecations():
                yield
        else:
            yield

    def test_proto_enum_matches_enum_name(self, pb_name: str) -> None:
        """Test that all known protobuf enum names match a Python member.

        Args:
            pb_name: The protobuf enum value name to check.
        """
        pb_value = self.proto_enum.Value(pb_name)
        stripped = pb_name.removeprefix(self.name_prefix)
        with self._maybe_ignore_deprecation(stripped):
            try:
                member = self.python_enum[stripped]
            except KeyError:
                # It is OK to have new protobuf enum values not yet in the Python
                # enum.
                return
            assert member.value == pb_value

    def test_proto_enum_matches_enum_value(self, pb_name: str) -> None:
        """Test that all known protobuf enum values match a Python member.

        Args:
            pb_name: The protobuf enum value name to check.
        """
        pb_value = self.proto_enum.Value(pb_name)
        stripped = pb_name.removeprefix(self.name_prefix)
        with self._maybe_ignore_deprecation(stripped):
            try:
                named_member = self.python_enum[stripped]
            except KeyError:
                try:
                    value_member = self.python_enum(pb_value)
                except ValueError:
                    # It is OK to have new protobuf enum values not yet in the
                    # Python enum.
                    return
                assert f"{self.name_prefix}{value_member.name}" == pb_name
                return
            assert named_member.value == pb_value

    def test_enum_matches_proto_enum_name(self, member: Enum) -> None:
        """Test that all Python enum members have a matching protobuf name.

        Args:
            member: The Python enum member to check.
        """
        pb_value = self.proto_enum.ValueType(member.value)
        pb_name = self.proto_enum.Name(pb_value)
        assert pb_name == f"{self.name_prefix}{member.name}"

    def test_enum_matches_proto_enum_value(self, member: Enum) -> None:
        """Test that all Python enum members have a matching protobuf value.

        Args:
            member: The Python enum member to check.
        """
        pb_value = self.proto_enum.Value(f"{self.name_prefix}{member.name}")
        assert member.value == pb_value

    def test_from_proto(self, pb_name: str) -> None:
        """Test conversion from protobuf returns a matching member or int.

        Args:
            pb_name: The protobuf enum value name to convert.
        """
        pb_value = self.proto_enum.Value(pb_name)
        stripped = pb_name.removeprefix(self.name_prefix)
        if stripped in self.deprecated_members:
            # Enum-level converter resolves the deprecated member and warns here
            # (not a raw int): the dataclass-level converter is what stores int 0.
            with pytest.warns(DeprecationWarning):
                result = self.from_proto(pb_value)
            assert isinstance(result, self.python_enum)
            assert result.value == pb_value
            assert result.name == stripped
            return
        with self._maybe_silence_converter_deprecation():
            result = self.from_proto(pb_value)
        if pb_value in [m.value for m in self.python_enum]:
            assert result is self.python_enum(pb_value)
        else:
            assert result == pb_value

    def test_from_proto_unknown(self) -> None:
        """Test conversion from protobuf for unknown values returns the int."""
        max_value = max(m.value for m in self.python_enum)
        unknown_pb_value = self.proto_enum.ValueType(max_value + 1)
        with self._maybe_silence_converter_deprecation():
            result = self.from_proto(unknown_pb_value)
        assert isinstance(result, int)
        assert result == unknown_pb_value

    def test_to_proto(self, member: Enum) -> None:
        """Test conversion to protobuf returns a matching protobuf value.

        Args:
            member: The Python enum member to convert.
        """
        with self._maybe_silence_converter_deprecation():
            pb_value = self.to_proto(member)
        assert pb_value == member.value

    def test_deprecated_members_warn(self) -> None:
        """Test that accessing every `deprecated_members` name warns."""
        for name in self.deprecated_members:
            with pytest.warns(DeprecationWarning):
                member = self.python_enum[name]
            assert member in self.python_enum

    def test_absent_members(self) -> None:
        """Test that every `absent_members` name is gone from the Python enum.

        The protobuf enum is still expected to define the former value, which no
        longer resolves to a Python member.
        """
        for name in self.absent_members:
            assert name not in self.python_enum.__members__
            pb_value = self.proto_enum.Value(f"{self.name_prefix}{name}")
            with pytest.raises(ValueError):
                self.python_enum(pb_value)
