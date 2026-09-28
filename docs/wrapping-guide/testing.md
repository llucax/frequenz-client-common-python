# Testing

Tests check that public Python wrappers keep working with generated protobuf
messages. Mirror the source layout, reuse the enum-parity helper, and check
warnings explicitly so the suite catches unwanted API changes early.

## Mirror the source tree

Mirror `src/frequenz/client/common/` under `tests/`, without that prefix. For
example, `src/frequenz/client/common/metrics/_thing.py` normally becomes
`tests/metrics/test_thing.py`. Drop the leading implementation underscore and
add the `test_` prefix. Keep the `proto/<namespace>/` directories. Split a
large source module into a matching test subdirectory when its types or
functions need separate files.

Use absolute public imports in tests. This checks that supported imports work.
It also stops a test from relying on an internal implementation-module path.

## Reuse enum parity tests

For an exported enum that matches a protobuf enum, subclass
[`EnumParityTest`][frequenz.client.common.test.enum_parity.EnumParityTest]. Set
its `python_enum`, `proto_enum`, `name_prefix`, `from_proto`, and `to_proto`
attributes. The inherited tests check wrapper member names and numbers,
known-value conversion, and unknown values. They intentionally accept generated
protobuf members that the wrapper does not expose yet, so a newer protobuf API
remains compatible with an older wrapper.

A protobuf API version that numbers a value differently from the wrapper enum
cannot use this helper, because the parity checks compare those numbers. Write
explicit tests for that version instead, pinning each generated value to the
member it converts to. [Enums](enums.md) explains when this happens.

## Treat documentation and warnings as tests

[Sybil](https://sybil.readthedocs.io/) collects Python examples in source
docstrings and checks that they pass some basic linter checks. Keep each example
self-contained and correct for its API. The test suite treats most warnings as
errors; deprecation warnings are configured separately and should be asserted
explicitly.

Assert each expected deprecation with
[`pytest.deprecated_call()`][pytest.deprecated_call]. This records the public
warning and stops an unrelated warning from being hidden. When deprecated code
correctly calls another deprecated symbol, suppress only that inner
`DeprecationWarning` in a small `frequenz.core.warnings.ignoring_deprecations()`
block to avoid duplicate messages. In a test, use the same small suppression
only for a warning that a dedicated assertion already checks, and check that a
replacement doesn't warn with `frequenz.core.warnings.asserting_no_deprecations()`.
Never suppress warnings globally, and never with
[`warnings.catch_warnings()`][warnings.catch_warnings]; [Deprecation and
compatibility](deprecation-and-compatibility.md) explains both helpers and why.
