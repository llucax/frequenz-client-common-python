# Deprecation and compatibility

Use these steps when you change a public wrapper type or conversion function.
They keep the old name visible and usable for a limited time. The upstream
[semantic-versioning rules](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/semver-0.x.x.md)
define the wider 0.x versioning process.

## Name the replacement precisely

Mark the old public symbol with
[`typing_extensions.deprecated`][typing_extensions.deprecated]. Use this exact
message form: `"<old FQCN> is deprecated since v<X.Y.Z>. Use [<new FQCN>][]
instead."`. Write both fully qualified names exactly, the old one plain and the
replacement as a bare cross-reference so the rendered `Deprecated:` admonition
links to it. The version belongs in the sentence: a separate "since" line
cannot be expressed through the decorator, so the two would drift apart.

The same string is printed as a runtime warning, so keep it to a sentence or
two and build it by concatenating single-line strings. A triple-quoted message
keeps its indentation, which stops the cross-reference from resolving and
prints an indented warning in the terminal. Do not put the names in backticks
either: they buy code font in the documentation at the cost of noise in the
console, where the reader cannot skip over them. Anything beyond "use X
instead", such as a change to the return type or behavior, goes in the
docstring body as prose. A caller should still know what to use from the
warning alone.

This example gives the replacement conversion function a numeric-suffixed name
and checks its warning:

```python
from pytest import deprecated_call
from typing_extensions import deprecated


def thing_from_proto2(value: int) -> str:
    return str(value)


@deprecated(
    "example.thing_from_proto is deprecated since v0.4.1. "
    "Use [example.thing_from_proto2][] instead."
)
def thing_from_proto(value: int) -> str:
    return thing_from_proto2(value)


with deprecated_call(
    match=r"^example\.thing_from_proto is deprecated since v0\.4\.1\. "
    r"Use \[example\.thing_from_proto2\]\[\] instead\.$"
):
    assert thing_from_proto(3) == "3"
```

`match` is a regular expression, so the brackets of the cross-reference have to
be escaped there, as do the dots of the qualified names.

The documentation build turns the decorator's message into a `Deprecated:`
admonition at the top of the symbol's docstring, and adds a `deprecated` label
next to its name. It reads the message from the source without running it, so
write it as string literals in the decorator call: a message held in a
constant, built by an f-string or returned by a helper function renders no
admonition at all.

Where no admonition can be generated, write the notice as a `Deprecated:`
admonition in the docstring instead. That is the case for a single argument,
construction that is being made stricter, a property (the decorator works at
runtime, but the documentation build ignores it there), and a message that is
not a literal. Put it immediately after the summary line and give it no custom
title (a title replaces the word "Deprecated" in the rendered output), and
again state the version in the text. Never hand-write one for a symbol that
already gets a generated one, or the page shows the same notice twice.

## Check downstream adoption before removal

When possible, check downstream client releases to see if they import or expose
a deprecated public type in public signatures before removing it. Remove the
type only after those clients have migrated, or keep a compatibility class
until the migration is complete. When a migration is expected to last long,
choose the removal point from downstream adoption and the support policy, not
from a fixed one-minor-release delay.

## Add a new converter when its contract changes

When a conversion function's arguments or return type change in an incompatible
way, add a new name with a numeric suffix such as `thing_from_proto2`. Keep the
previous name as a deprecated function. The new function has its own stable
signature and can return the current `X | InvalidX` result described in
[Conversion functions](conversion-functions.md).

The numeric suffix supports the compatibility transition; it is not necessarily
permanent. At the next minor release, follow the upstream
[semantic-versioning rules](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/semver-0.x.x.md)
for removing deprecated versions and, when applicable, restoring the
unsuffixed name while retaining a deprecated alias for the suffixed name.

For an enum-member change, use
[`deprecated_member`][frequenz.core.enum.deprecated_member]. It keeps the old
member temporarily and warns when code uses it. Its message follows the same
form as the decorator's and gets the same generated admonition and label, as
long as it is written as string literals in the call. Document the
representation new code should use.

A renamed member keeps its old name as a deprecated alias of the same value,
which [`unique`][frequenz.core.enum.unique] allows:

```python
from frequenz.core.enum import Enum, deprecated_member, unique


@unique
class Mode(Enum):
    """Modes a thing can run in."""

    NEW_NAME = 1
    """The thing runs normally."""

    OLD_NAME = deprecated_member(
        1,
        "example.Mode.OLD_NAME is deprecated since v0.5.0. "
        "Use example.Mode.NEW_NAME instead.",
    )
    """Old name of `NEW_NAME`."""
```

## Keep a moved symbol importable

When a public symbol moves to another module, keep its old import path working
with `frequenz.core.warnings.deprecated_aliases()` instead of writing a module
`__getattr__` by hand. The alias is the very same object, so
[`isinstance()`][isinstance] keeps working through both paths, and the
documentation build generates the admonition and label for every alias, as
long as it is a literal in the call.

```python
from typing import TYPE_CHECKING, TypeAlias

from frequenz.core.warnings import DeprecatedAlias, deprecated_aliases

if TYPE_CHECKING:
    from example.new import Thing as _Thing

    Thing: TypeAlias = _Thing
    """A thing, now living in `example.new`."""
else:
    __getattr__ = deprecated_aliases(
        __name__,
        DeprecatedAlias("Thing", new_module="example.new", since="v0.5.0"),
    )
```

Keep that structure exactly: without the `else:`, type checkers see the
`__getattr__` and treat every name in the module as `Any`. When the symbol was
renamed too, give its new name as `new_name`; without `new_module`, the alias
points at a renamed symbol in its own module. Each alias gives
its own `since`, the version it is deprecated in, so aliases deprecated in
different releases can each say theirs; the warning and the generated
admonition both read `{old} is deprecated since {since}. Use {new} instead.`
When that standard wording is not enough, give `message` instead of `since`,
a full template taking only `{old}` and `{new}`, the two fully qualified
names; the documentation turns `{new}` into a link there too, so leave out
the cross-reference brackets.

An alias only fits when the old name can be the same object as the new one.
When the old type has to stay distinct, as
[`ComponentId`][frequenz.client.common.microgrid.components.ComponentId] does
next to
[`ElectricalComponentId`][frequenz.client.common.microgrid.electrical_components.ElectricalComponentId],
keep a deprecated class instead.

## Silence only the deprecations you raise yourself

Sometimes library code has to touch a symbol it deprecated itself, such as a
deprecated converter that still has to build the deprecated type it returns.
The caller already gets the converter's own warning, so a second one from
inside it is noise. Silence it with
`frequenz.core.warnings.ignoring_deprecations()`, around the statement that
raises it and nothing more, so deprecations from anywhere else still get
through:

```python
from frequenz.core.warnings import ignoring_deprecations
from typing_extensions import deprecated

from example import OldThing, ThingProto


@deprecated(
    "example.old_thing_from_proto is deprecated since v0.5.0. "
    "Use example.thing_from_proto instead."
)
def old_thing_from_proto(message: ThingProto) -> OldThing:
    """Convert a protobuf message to the deprecated `OldThing`."""
    with ignoring_deprecations():
        return OldThing(value=message.value)
```

The same applies to code that is not deprecated itself but still has to accept
or build a deprecated symbol for compatibility: the user is warned where they
use the deprecated symbol, not by the library's internals.

Do not use [`warnings.catch_warnings()`][warnings.catch_warnings] for this.
Entering and leaving it resets the warnings deduplication history of the whole
program ([python/cpython#73858](https://github.com/python/cpython/issues/73858)),
so every warning that was already shown, by this library or any other code, is
shown again after each call. In an application converting data in a loop, that
turns a handful of warnings into tens of thousands.

## Tighten invariants in stages

When you tighten a rule, do not always reject old input immediately. First,
accept it and emit a [`DeprecationWarning`][] with
[`warnings.warn()`][warnings.warn]. Where feasible, provide a documented opt-in
flag for the stricter behavior. In a later minor release, make invalid normal
construction raise every time. A conversion function must still keep invalid
protobuf data in the typed invalid result from
[Validity in the type](validity-in-the-type.md).

This lets callers find affected construction code when warnings are errors. They
can test the stricter behavior before it becomes required and migrate on purpose.

## Test and document each transition

Test every public deprecation with
[`pytest.deprecated_call()`][pytest.deprecated_call]. Check the exact message
and the replacement behavior. The outer API must still emit its one public
warning, even when it silences inner ones as described above.

Check that the replacement doesn't go through anything deprecated with
`frequenz.core.warnings.asserting_no_deprecations()`, rather than with an
`"error"` filter. The filter turns the warning into an exception inside the
code under test, where a broad `except` can swallow it; the helper records the
warnings instead and fails when the block ends, listing each one and where it
came from:

```python
from frequenz.core.warnings import asserting_no_deprecations

from example import thing_from_proto2


def test_thing_from_proto2_does_not_warn() -> None:
    with asserting_no_deprecations():
        assert thing_from_proto2(3) == "3"
```

Add `RELEASE_NOTES.md` migration bullets that state the old behavior, the
replacement, what changes, and the planned removal version. Remove the
deprecated name at the right minor-version bump. Follow the upstream
[semantic-versioning rules](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/semver-0.x.x.md).
