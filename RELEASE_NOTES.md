# Frequenz Client Common Library Release Notes

> [!IMPORTANT]
> This release adopted `frequenz.core.typing.FloatInt`, a type alias for `float | int`, for annotations that may contain either floating-point or integer values.
>
> PEP 484's [numeric tower](https://peps.python.org/pep-0484/#the-numeric-tower) makes `int` assignable wherever `float` is annotated, while at runtime `isinstance(1, float)` is `False` — so a plain `float` annotation silently admits values that crash `match … case float():` arms and `float`-only methods like `hex()`. The library now annotates `floats` with `FloatInt` instead. See [`FloatInt` documentation](https://frequenz-floss.github.io/frequenz-core-python/v1.4/reference/frequenz/core/typing/#frequenz.core.typing.FloatInt) for details.

## Summary

> [!NOTE]
> Despite the patch version number, this is a huge release: 58 pull requests and over 320 commits, adding about 6,000 lines to the library, 9,000 lines of tests and 1,800 lines of documentation. It realizes the new library design while keeping backwards compatibility with v0.4.0; the remaining (breaking) cleanup of everything deprecated here will follow in v0.5.0.

The release brings the wrappers for the Microgrid and Assets APIs (`Microgrid`, `Location`, `Lifetime`, and the whole `ElectricalComponent` class hierarchy with its connections) and settles how invalid wire data is handled: conversion functions no longer raise or report issues through side channels, they return an `Invalid*` representation instead, and safe `get_*()` accessors raise clear exceptions. Every `UNSPECIFIED` enum member, the electrical component category and type enums, and the `*_with_issues()` and single-return converters they replace are deprecated and scheduled for removal in v0.5.0.

It also introduces 3 new guides in the documentation: a User Guide for users of the wrapper types, a Client Developer Guide for `frequenz-client-*` library authors, and a Wrapping Guide for anyone designing a wrapper.

There are a few intentional hard breaks too, all listed in the Upgrading section: `MetricSample.bounds` became `bounds_set`, `MetricSample.sample_time` became `sample_time2`, `MetricConnection.name` is no longer optional, and some constructors that silently accepted invalid values now raise.

## Upgrading

* `frequenz.client.common.microgrid.components.ComponentId` is restored as a deprecated compatibility class. It keeps its historical import path and remains a distinct type from `ElectricalComponentId`. This restores only `ComponentId`, not the removed `ComponentCategory`, `ComponentStateCode` or `ComponentErrorCode` symbols. The v0.4.0 release remains incompatible with users of the removed import path. Removal will be coordinated with downstream migration rather than tied automatically to v0.5.0.

* `frequenz.client.common.microgrid.electrical_components.ElectricalComponentId` now renders with the prefix `ECID` instead of `CID` (for example, `ECID42` instead of `CID42`).

    This is a display-only change.

    Anyone who adopted v0.4.0 and logs or displays an `ElectricalComponentId` will see `ECID42` where they previously saw `CID42`. No code changes are needed, only an update to any log-parsing rules or UI labels that checked for the `CID` prefix.

* The `frequenz.client.common.microgrid.electrical_components.ElectricalComponentCategory` enum is now deprecated and will be removed in a future release.

    Accessing any member of this enum will emit a `DeprecationWarning`. Users are encouraged to switch to the `ElectricalComponent` class hierarchy (using `match` expressions or `isinstance()`) to identify components.

    Client implementers: To convert a component class to the protobuf enum values the server expects, use the new `electrical_component_class_to_proto()` / `electrical_component_class_from_proto()` converters (see New Features).

    For example, instead of:

    ```text
    def filter_by(category: ElectricalComponentCategory) -> ...:
        ...
    ```

    Use:

    ```text
    def filter_by(component: ElectricalComponentTypes | type[ConvertibleElectricalComponentTypes]) -> ...:
        category_value, sub_type_value = electrical_component_class_to_proto(component)
        ...
    ```

    The related proto-layer converters (`electrical_component_category_to_proto`, `electrical_component_category_from_proto`) are also deprecated.

* The `UNSPECIFIED` members in the following enums are now deprecated:

    * `frequenz.client.common.grid.EnergyMarketCodeType`
    * `frequenz.client.common.metrics.Metric`
    * `frequenz.client.common.metrics.MetricConnectionCategory`
    * `frequenz.client.common.microgrid.electrical_components.ElectricalComponentDiagnosticCode`
    * `frequenz.client.common.microgrid.electrical_components.ElectricalComponentStateCode`
    * `frequenz.client.common.streaming.Event`

    When loading these types from protobuf using dataclass-level converters (e.g., `delivery_area_from_proto`, `metric_sample_from_proto`), the low-level fields (`code_type`, `category`, `metric`, and the keys of `ElectricalComponent.metric_config_bounds`) now store the raw integer `0` for unspecified values instead of the deprecated member. Unspecified values should be rare errors, so it is better to expose them only via the low-level interface.

    Lower-level enum-level converters still return the deprecated member.

    Users are encouraged to switch from direct field access to the new `get_*()` methods (see New Features), which provide a safer way to handle unspecified or unrecognized values.

* `frequenz.client.common.grid.proto.v1alpha8.delivery_area_from_proto` is now deprecated; use `delivery_area_from_proto2` instead.

    The new converter returns `DeliveryArea | InvalidDeliveryArea` and surfaces malformed wire data at the type level rather than silently constructing a `DeliveryArea` with invalid content. The old converter continues to work but emits a `DeprecationWarning`.

* `frequenz.client.common.grid.DeliveryArea` construction with invalid data is deprecated. Please construct only valid `DeliveryArea` objects.

    A well-formed `DeliveryArea` has a non-empty `code` and a specified (non-`UNSPECIFIED`) `code_type`. Constructing one with invalid data currently emits a `DeprecationWarning`; a future release will replace the warning with a hard `ValueError`. To opt into the upcoming behavior right now, pass `_raise_on_invalid=True` to the constructor. Prefer `delivery_area_from_proto2` to load delivery areas from the wire — malformed messages become `InvalidDeliveryArea` instances instead.

* `frequenz.client.common.pagination.proto.v1alpha8.pagination_info_from_proto` is now deprecated; use `pagination_info_from_proto2` instead.

    The new converter returns `PaginationInfo | InvalidPaginationInfo` and surfaces malformed wire data at the type level rather than raising a `ValueError` when `total_items` is negative. It also reads `next_page_token` through `HasField()`, so a token the server actually sent is preserved even when it is empty; only an unset token becomes `None`. The old converter continues to work but emits a `DeprecationWarning`.

* `frequenz.client.common.pagination.PaginationInfo` now raises a `ValueError` when `total_items` is negative, which v0.4.0 accepted silently.

    A count of items can't be negative. Use `pagination_info_from_proto2` to load pagination information from the wire — malformed messages become `InvalidPaginationInfo` instances instead of raising.

* `frequenz.client.common.metrics.proto.v1alpha8.bounds_from_proto` is now deprecated; use `bounds_from_proto2` instead.

    The new converter returns `Bounds | InvalidBounds` and surfaces malformed wire data at the type level rather than raising a `ValueError` when `lower > upper`. The old converter continues to work but emits a `DeprecationWarning`.

* `frequenz.client.common.metrics.proto.v1alpha8.bounds_from_proto_with_issues` is now deprecated with no direct replacement.

    Validity is now encoded in the return type of `bounds_from_proto2` (`Bounds | InvalidBounds`), so callers should inspect the returned type instead of collecting issue strings via a side channel. The old converter continues to work but emits a `DeprecationWarning`.

* `frequenz.client.common.metrics.proto.v1alpha8.metric_sample_from_proto_with_issues` and `metric_connection_from_proto_with_issues` are now deprecated; use `metric_sample_from_proto` and `metric_connection_from_proto` instead.

    The new converters (see New Features) encode an unspecified or unrecognized `metric` / `category` as a raw `int` (`Metric | int` / `MetricConnectionCategory | int`) and malformed bounds as an `InvalidBoundsSet` in the returned object, so callers inspect validity on the returned type instead of collecting issue strings via a side channel. The old converters continue to work but emit a `DeprecationWarning`.

* `frequenz.client.common.metrics.Bounds` now raises `ValueError` when constructed with a `NaN` endpoint (`lower` or `upper`), as it did already when `lower > upper`. A `NaN` endpoint made every membership test meaningless, so this was never a usable value. Use `None` for an unbounded direction, and `bounds_from_proto2` to load bounds from the wire, which returns `InvalidBounds` instead of raising.

* `frequenz.client.common.metrics.MetricConnection.name` is now a plain `str` defaulting to `""` instead of `str | None` defaulting to `None`, mirroring the protobuf field, which has no presence and reads as `""` when unset.

    This is an intentional hard break of the released dataclass API (following the project's [0.x compatibility guidance](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/semver-0.x.x.md)): passing `name=None` is now a type error, `connection.name is None` checks never match anymore (use `not connection.name`), and instances built with the old default no longer compare equal to instances built with the new one.

* `frequenz.client.common.metrics.Bounds.__str__` now renders as `[lower,upper]` (no space after the comma) to match the compact format used by `Lifetime` and to compose cleanly with the `<invalid:...>` marker on `InvalidBounds`.

* Several `__str__` representations were standardized around the `<invalid:VALUE>` marker, so a `grep '<invalid:'` over logs finds every invariant violation regardless of which type produced it:

    * `frequenz.client.common.metrics.MetricConnection.__str__` renders as `{name}:{category}` (with `name` possibly empty); known categories render as their member name, the unspecified category renders as `cat=<invalid:0>`, and unknown non-zero categories render as `cat=<int>`.
    * `frequenz.client.common.metrics.MetricSample` gained a compact `__str__` (`metric=value`, plus `@connection` when a connection is set) instead of falling back to the dataclass `repr`.
    * `UnrecognizedElectricalComponent`, `MismatchedCategoryElectricalComponent`, `UnrecognizedBattery`, `UnrecognizedEvCharger` and `UnrecognizedInverter` now expose their raw wire `category` / `type` in `__str__` (e.g. `ECID1:comp1:Inverter:type=99`), instead of hiding it behind the class name alone. These values are merely unrecognized (forward-compatible), not invariant violations, so they use a plain `:field=value` detail rather than the `<invalid:...>` marker.

* `frequenz.client.common.metrics.MetricSample.bounds` is now deprecated; use `bounds_set` instead.

    The field type changed from `list[Bounds]` to `BoundsSet | InvalidBoundsSet` (see New Features), and `bounds` is now a deprecated read-only property backed by `bounds_set`, not a real dataclass field. Basic reads and construction still work: passing the `bounds=` keyword argument builds a `BoundsSet` (emitting a `DeprecationWarning`), and reading `MetricSample.bounds` returns the valid `Bounds` as a normalized, merged `list` (also emitting a `DeprecationWarning`), so it may differ from the raw wire list when bounds overlapped or touched.

    Because `bounds` is no longer a real field, this is an intentional hard break of the released dataclass API (following the project's [0.x compatibility guidance](https://github.com/frequenz-floss/docs/blob/v0.x.x/python/semver-0.x.x.md)), not a transparent shim. Several behaviors that worked with the previous `list[Bounds]` field no longer do:

    * `dataclasses.fields(sample)`, `dataclasses.asdict(sample)` and `dataclasses.astuple(sample)` no longer include `bounds` (only `bounds_set`), so e.g. `dataclasses.asdict(sample)["bounds"]` now raises `KeyError`.
    * `dataclasses.replace(sample, bounds=...)` raises `TypeError`, because the copied-over `bounds_set` field and the deprecated `bounds` argument cannot both be supplied.
    * In-place mutation such as `sample.bounds.append(...)` no longer affects the sample: the property returns a fresh list on every read.
    * Equality, hashing, list length and ordering may differ from the old raw list, because overlapping or touching bounds are merged and sorted on construction, and malformed bounds are dropped from the property.
    * Old pickles carrying a `bounds` field will not round-trip.

    Migrate to `bounds_set` (or `get_bounds_set()`) for all of these.

* `frequenz.client.common.proto.datetime_from_proto` is now deprecated; use `datetime_from_proto2` instead.

* `frequenz.client.common.metrics.MetricSample.sample_time` is now a deprecated read-only property; use the new `get_sample_time()` method instead, or the new `sample_time2` field to also see malformed timestamps.

    The field became `datetime | InvalidDatetime`, which the released `datetime` annotation cannot express, so it was renamed. Reading `sample_time` still returns a `datetime` and now emits a `DeprecationWarning`; for a malformed wire timestamp it raises `InvalidDatetimeError` (a `ValueError`) rather than returning a repaired value. `get_sample_time()` does the same without the warning, which is why the warning recommends it.

    Constructing with `sample_time=` is **not** deprecated and keeps working: it accepts a well-formed `datetime` today and will accept the wider type once `sample_time2` is renamed back to `sample_time`. Use `sample_time2=` to build a sample from a malformed wire timestamp.

    Because `sample_time` is no longer a real field, `dataclasses.fields()`, `asdict()`, `astuple()` and `replace()` see `sample_time2`.

* `frequenz.client.common.metrics.proto.v1alpha8.metric_sample_from_proto_with_issues` no longer drops invalid bounds or reports them as a major issue.

    Malformed bounds are now preserved in the returned `MetricSample.bounds_set` as an `InvalidBoundsSet` (validity is encoded in the type), so the previous "bounds for ... is invalid, ignoring these bounds" major issue is no longer produced.

    This changes the converter's diagnostic contract: callers that used a non-empty `major_issues` list as their sample-acceptance gate will no longer see malformed bounds rejected there, and must instead inspect `bounds_set` (or call `get_bounds_set()`, which raises `InvalidBoundsSetError`) to detect them. This is an intentional trade-off — bounds validity now lives in the return type rather than the issue side-channel.

* `float`-typed fields and accessors are now annotated with `FloatInt` (`float | int`).
  These symbols are affected:

    * `frequenz.client.common.metrics.AggregatedMetricValue`: the `avg`, `min`, `max` and `raw` fields.
    * `frequenz.client.common.metrics.MetricSample`: the `value` field and the `as_single_value()` return type.
    * `frequenz.client.common.metrics.Bounds`: the `lower` and `upper` fields (shared with the new `BaseBounds` / `InvalidBounds` hierarchy).

    Runtime behavior is completely unchanged: these fields could always end up storing `int` values (`x: float = 1` is legal even under `mypy --strict`).

## New Features

* Added 4 new electrical component classes for categories that previously collapsed into `UnrecognizedElectricalComponent`:

    * `frequenz.client.common.microgrid.electrical_components.Plc` (PLC, category 13)
    * `frequenz.client.common.microgrid.electrical_components.StaticTransferSwitch` (category 15)
    * `frequenz.client.common.microgrid.electrical_components.UninterruptiblePowerSupply` (UPS, category 16)
    * `frequenz.client.common.microgrid.electrical_components.CapacitorBank` (category 17)

* Added two new proto-layer converters in `frequenz.client.common.microgrid.electrical_components.proto.v1alpha8`:

    * `electrical_component_class_to_proto(component_class)` — converts a `ValidElectricalComponentTypes` class to the `(category, sub_type)` protobuf enum value tuple the server expects. Implemented with raw proto constants only (no deprecated wrapper enums), so it will continue to work after the wrapper enums are removed.
    * `electrical_component_class_from_proto(category, sub_type=None)` — converts a raw `(category, sub_type)` protobuf enum value pair back to the corresponding `ConcreteElectricalComponentTypes` class.

    Added a few new type aliases to support them. In particular `frequenz.client.common.microgrid.electrical_components.proto.v1alpha8.ConvertibleElectricalComponentTypes` is the most useful (see Upgrading section above).

* Added new exceptions:

    * `frequenz.client.common.ClientCommonError` as a base exception for the package.
    * `frequenz.client.common.InvalidAttributeError` as a base for all exceptions raised when an invalid attribute is encountered. Inherits also from `ValueError` for convenience.
    * `frequenz.client.common.MissingFieldError` for accessors that resolve a `T | ... | None` wrapper field to a concrete value and see `None` because the underlying field was not set on the wire.
    * `frequenz.client.common.UnspecifiedEnumValueError` for unspecified enum values (raw `0` or the deprecated member).
    * `frequenz.client.common.UnrecognizedEnumValueError` for enum members not yet recognized by the library. Carries the raw integer value in its `value` attribute.

* Added safe convenience getters that raise the new exceptions for unspecified, unrecognized, missing or invalid values:

    * `frequenz.client.common.grid.DeliveryArea.get_code_type()`
    * `frequenz.client.common.metrics.MetricConnection.get_category()`
    * `frequenz.client.common.metrics.MetricSample.get_metric()`
    * `frequenz.client.common.metrics.MetricSample.get_bounds_set()`
    * `frequenz.client.common.metrics.MetricSample.get_sample_time()`
    * `frequenz.client.common.microgrid.electrical_components.ElectricalComponent.get_metric_config_bounds()`

* Added `frequenz.client.common.InvalidDatetime`, a protobuf-independent wrapper preserving the raw `seconds` and `nanos` of a wire timestamp that is not a well-formed protobuf `Timestamp`, and `frequenz.client.common.InvalidDatetimeError`, raised by the safe accessors for those fields. Both are exported from the top-level package, not from `frequenz.client.common.types`, because a timestamp is not a `frequenz-api-common` message. See the Upgrading section for the fields that can now hold one.

* Added `frequenz.client.common.metrics.MetricSample.sample_time2`, typed `datetime | InvalidDatetime`, replacing the now-deprecated `sample_time` property (see Upgrading).

* Added `frequenz.client.common.proto.datetime_from_proto2` returning `datetime | InvalidDatetime`. This is the replacement for the now-deprecated `datetime_from_proto`.

* Added new delivery-area class hierarchy:

    * `frequenz.client.common.grid.BaseDeliveryArea` — abstract common supertype of the two concrete leaves; not directly instantiable.
    * `frequenz.client.common.grid.DeliveryArea` — well-formed delivery area (retroactively made a subclass of `BaseDeliveryArea`).
    * `frequenz.client.common.grid.InvalidDeliveryArea` — malformed wire data; same fields as `DeliveryArea` with no invariants enforced, so callers can inspect whatever the server actually sent.

* Added `frequenz.client.common.grid.proto.v1alpha8.delivery_area_from_proto2` returning `DeliveryArea | InvalidDeliveryArea`. This is the replacement for the now-deprecated `delivery_area_from_proto`.

* Added a new pagination-info class hierarchy:

    * `frequenz.client.common.pagination.BasePaginationInfo` — abstract common supertype of the two concrete leaves; not directly instantiable.
    * `frequenz.client.common.pagination.PaginationInfo` — well-formed pagination information (retroactively made a subclass of `BasePaginationInfo`), now with a compact `__str__` rendering as `items=100,next=token`.
    * `frequenz.client.common.pagination.InvalidPaginationInfo` — malformed wire data; same fields as `PaginationInfo` with no invariants enforced, rendering a negative count as `items=<invalid:-1>`.

* Added `frequenz.client.common.pagination.proto.v1alpha8.pagination_info_from_proto2` returning `PaginationInfo | InvalidPaginationInfo`. This is the replacement for the now-deprecated `pagination_info_from_proto`.

* Added a new `frequenz.client.common.microgrid.Lifetime` type together with the `frequenz.client.common.microgrid.proto.v1alpha8.lifetime_from_proto` conversion function.

* Added `frequenz.client.common.metrics.proto.v1alpha8.bounds_from_proto2` returning `Bounds | InvalidBounds`. This is the replacement for the now-deprecated `bounds_from_proto`.

* `frequenz.client.common.metrics.Bounds` gained containment check capabilities:

    * `value in bounds` (`__contains__`) tests membership, inclusive on both ends, with a `None` bound meaning unbounded in that direction. Any `FloatInt` value is accepted, including integers too large to fit in a `float`.
    * `bool(bounds)` and `bounds.is_bounded()` report whether the bounds restrict anything; a fully unbounded `Bounds()` is falsy. A `-inf` lower or `+inf` upper endpoint is canonicalized to `None` (unbounded) on construction, so `Bounds(lower=-math.inf, upper=math.inf)` equals `Bounds()`; a wrong-side infinity (`+inf` lower or `-inf` upper) is kept as a real endpoint.

* Added a new bounds-set class hierarchy:

    * `frequenz.client.common.metrics.BoundsSet` — a normalized union of `Bounds` with an efficient `value in bounds_set` membership test. Overlapping and touching bounds are merged on construction, and the empty set is the unbounded set.
    * `frequenz.client.common.metrics.InvalidBoundsSet` — a set built from bounds that included at least one `InvalidBounds`; it preserves all the raw bounds unmerged and provides no membership test.
    * `frequenz.client.common.metrics.proto.v1alpha8.bounds_set_from_proto` conversion function returning `BoundsSet | InvalidBoundsSet`. It converts a `repeated Bounds` field into a single bounds set.

* Added a new `frequenz.client.common.metrics.MetricSample.bounds_set` field, typed `BoundsSet | InvalidBoundsSet`, replacing the deprecated `bounds` list (see Upgrading). Malformed wire bounds are preserved as an `InvalidBoundsSet` instead of being dropped. Use `get_bounds_set()` to resolve it to a valid `BoundsSet` or a clear `InvalidBoundsSetError`.

* Added `frequenz.client.common.metrics.proto.v1alpha8.metric_sample_from_proto` and `metric_connection_from_proto`, dataclass-level converters returning `MetricSample` and `MetricConnection` with validity encoded in the return type: an unspecified or unrecognized `metric` / `category` is kept as a raw `int` (`Metric | int` / `MetricConnectionCategory | int`) and malformed bounds as an `InvalidBoundsSet`, so callers inspect the returned object (or the `get_*()` accessors) rather than collecting issue strings via a side channel.

* Added a new `frequenz.client.common.types.Location` type together with the `frequenz.client.common.types.proto.v1alpha8.location_from_proto` conversion function.

* Added a new `frequenz.client.common.microgrid.Microgrid` type with a raising `is_active()` method, together with the `frequenz.client.common.microgrid.proto.v1alpha8.microgrid_from_proto` conversion function.

* Added a new `frequenz.client.common.microgrid.sensors.Sensor` type, with an `operational_lifetime` typed `Lifetime | InvalidLifetime` and the raising `get_operational_lifetime()`, `is_operational_at()` and `is_operational_now()` accessors, together with the `frequenz.client.common.microgrid.sensors.proto.v1alpha8.sensor_from_proto` conversion function.

* Added a new `frequenz.client.common.microgrid.electrical_components` package, featuring a `ElectricalComponent` class hierarchy and its families (battery, inverter, EV charger, etc.), and `ElectricalComponentConnection` class hierarchy, including `v1alpha8` proto conversion functions.

    The class of a component is its identity; components don't carry category or type attributes. The only exceptions are the error-recovery classes `UnrecognizedElectricalComponent` and `MismatchedCategoryElectricalComponent` (with a raw protobuf `category` value) and `UnrecognizedBattery`, `UnrecognizedInverter` and `UnrecognizedEvCharger` (with a raw protobuf `type` value), which preserve the raw protobuf values received from the protocol version used to load them.

    Components also expose the raising boolean accessors `provides_telemetry()` and `accepts_control()`, the category-specific fields as a `CategorySpecificInfo` (with the protobuf field names as keys for the fields this library doesn't wrap yet), and the metric configuration bounds aggregated per metric into a `BoundsSet | InvalidBoundsSet`.

* Added smaller supporting types, each following the same validity-in-the-type pattern as the ones above:

    * `frequenz.client.common.types.InvalidLatitude`, `InvalidLongitude` and `InvalidCountryCode`, held by `Location` when the wire value is out of range or malformed, with the matching `InvalidLatitudeError`, `InvalidLongitudeError` and `InvalidCountryCodeError` raised by `Location.get_latitude()`, `get_longitude()`, `get_country_code()` and `get_country_code_or_none()`.
    * `frequenz.client.common.microgrid.InvalidLifetime`, returned by `lifetime_from_proto` for a malformed lifetime, and `InvalidLifetimeError`, raised by the accessors resolving one.
    * `frequenz.client.common.microgrid.electrical_components.CategorySpecificInfo`, the container for the category-specific fields of an `ElectricalComponent`.

* Added three authored documentation guides, one per audience:

    * **User Guide** — For users of the wrapper types: typed IDs, safe accessors and exceptions, numeric types, enum-or-int fields, validity in the type, membership and bounds, reading string output, and an overview of the available wrappers.
    * **Client Developer Guide** — For `frequenz-client-*` library authors: which versioned `proto.v1alphaN` package to import, the usual client-method shapes, what this library already converts, and when to write your own wrappers.
    * **Wrapping Guide** — For anyone designing a wrapper: package layout, enum representation, data types, validity in the type, conversion functions, deprecation, and testing. The field-name and docstring rules previously listed in `CONTRIBUTING.md` moved here.

## Bug Fixes

* Fixed `EnumParityTest` so protobuf values whose Python member name exists with a different number fail parity checks instead of being treated as unmirrored protobuf values.
* Fixed potential unexpected exceptions due to type-checking accepting `int` for code annotated to only accept `float`. Fixes #250.
* Exception messages reporting an invalid value now use its `str()` instead of its `repr()`, so they show the compact `<invalid:...>` rendering instead of a verbose dataclass dump.
* Fixed warnings being shown over and over instead of once. The library silenced its own internal deprecation warnings with `warnings.catch_warnings()`, which resets the warnings deduplication history of the whole program every time it is used ([python/cpython#73858](https://github.com/python/cpython/issues/73858)), so every warning already shown, from this library or any other code, was shown again on each call to a converter, accessor or `str()`. It now uses `frequenz.core.warnings.ignoring_deprecations()`, which leaves that history alone.
