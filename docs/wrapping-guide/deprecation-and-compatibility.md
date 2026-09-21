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
and the replacement behavior. If deprecated code correctly calls another
deprecated symbol, suppress only that expected inner
[`DeprecationWarning`][]
in a small [`warnings.catch_warnings()`][warnings.catch_warnings] block. The
outer API must still emit its one public warning.

Add `RELEASE_NOTES.md` migration bullets that state the old behavior, the
replacement, what changes, and the planned removal version. Remove the
deprecated name at the right minor-version bump. Follow the upstream
[semantic-versioning rules](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/semver-0.x.x.md).
