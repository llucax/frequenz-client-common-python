# Deprecation and compatibility

Use these steps when you change a public wrapper type or conversion function.
They keep the old name visible and usable for a limited time. The upstream
[semantic-versioning rules](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/semver-0.x.x.md)
define the wider 0.x versioning process.

How to deprecate a Python symbol in general, and which texts it needs, is in
the [deprecations guide](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/deprecations.md).
Read it first: this page only adds what is specific to wrappers and conversion
functions.

## Name the replacement precisely

Mark the old public symbol with
[`typing_extensions.deprecated`][typing_extensions.deprecated], as the
deprecations guide asks, and give it the two texts it describes: a plain text
warning, and a `Deprecated:` notice in the docstring. In this library:

* Write the warning as `"<old FQCN> is deprecated. Use <new FQCN> instead."`,
  with both fully qualified names written exactly. Leave out the version and
  any Markdown, since it is read in a terminal. A caller should know what to
  use from the warning alone, so name the replacement even when the notice
  links to a longer explanation.
* Write the notice by hand, right after the summary line, as `Deprecated since
  v<X.Y.Z>. Use [`<new name>`][<new FQCN>] instead.`. Write the link as the
  absolute path of the replacement: this repository doesn't allow relative
  cross-references. Anything beyond "use X instead", such as a change to the
  return type or behavior, goes in the docstring body as prose.
* A notice about part of a symbol says which part: the `bounds` argument of a
  constructor, or constructing a type with invalid data while the type itself
  stays.

This example gives the replacement conversion function a numeric-suffixed name
and checks its warning:

```python
from pytest import deprecated_call
from typing_extensions import deprecated


def thing_from_proto2(value: int) -> str:
    return str(value)


@deprecated(
    "example.thing_from_proto is deprecated. "
    "Use example.thing_from_proto2 instead."
)
def thing_from_proto(value: int) -> str:
    """Convert a value to a string.

    Deprecated:
        Deprecated since v0.4.1. Use
        [`thing_from_proto2`][example.thing_from_proto2] instead.
    """
    return thing_from_proto2(value)


with deprecated_call(
    match=r"^example\.thing_from_proto is deprecated\. "
    r"Use example\.thing_from_proto2 instead\.$"
):
    assert thing_from_proto(3) == "3"
```

`match` is a regular expression, so the dots of the qualified names have to be
escaped there.

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
[`deprecated_member`][frequenz.core.enum.deprecated_member], as the deprecations
guide describes. It keeps the old member temporarily and warns when code uses
it. Document the representation new code should use.

The `UNSPECIFIED` members of the enums here have no member to point at, since
the replacement is the integer `0`, so they pass their own message as a string
literal and get a hand-written notice:

```python
from frequenz.core.enum import Enum, deprecated_member, unique


@unique
class Mode(Enum):
    """Modes a thing can run in."""

    UNSPECIFIED = deprecated_member(
        0,
        "example.Mode.UNSPECIFIED is deprecated. "
        "Use the int value 0 instead if you really need to check for this "
        "low-level value.",
    )
    """The mode is unspecified.

    Deprecated:
        Deprecated since v0.5.0. Use the int value `0` instead if you really
        need to check for this low-level value.
    """

    NORMAL = 1
    """The thing runs normally."""
```

When many members share one long explanation, as every member of the deprecated
`ElectricalComponentCategory` does, explain it once in the notice of the enum
and have each member's notice link to it. Each warning still explains it in
full, since it can't be followed like a link.

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
