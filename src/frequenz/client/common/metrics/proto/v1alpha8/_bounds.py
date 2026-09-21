# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of Bounds objects from protobuf messages."""

from collections.abc import Sequence
from typing import assert_never

from frequenz.api.common.v1alpha8.metrics import bounds_pb2
from typing_extensions import deprecated

from ..._bounds import Bounds, BoundsSet, InvalidBounds, InvalidBoundsSet


@deprecated(
    "frequenz.client.common.metrics.proto.v1alpha8.bounds_from_proto is "
    "deprecated since v0.4.1. Use "
    "[frequenz.client.common.metrics.proto.v1alpha8.bounds_from_proto2][] "
    "instead."
)
def bounds_from_proto(message: bounds_pb2.Bounds) -> Bounds:  # noqa: DOC502
    """Create a [`Bounds`][....Bounds] object from a protobuf message.

    [`bounds_from_proto2`][..bounds_from_proto2] distinguishes well-formed from
    malformed data at the type level (`Bounds | InvalidBounds`) rather than
    raising a `ValueError` when the invariant fires.

    Args:
        message: The protobuf message to convert.

    Returns:
        The corresponding [`Bounds`][....Bounds] object.

    Raises:
        ValueError: If the message is not valid.
    """
    return Bounds(
        lower=message.lower if message.HasField("lower") else None,
        upper=message.upper if message.HasField("upper") else None,
    )


def bounds_from_proto2(
    message: bounds_pb2.Bounds,
) -> Bounds | InvalidBounds:
    """Create bounds from a protobuf message, preserving malformed data.

    Args:
        message: The protobuf message to convert.

    Returns:
        A [`Bounds`][....Bounds] when the values form a valid range, or an
            [`InvalidBounds`][....InvalidBounds] preserving values that
            violate `lower <= upper`. A present but empty protobuf message
            becomes an unbounded `Bounds()`.
    """
    lower = message.lower if message.HasField("lower") else None
    upper = message.upper if message.HasField("upper") else None
    try:
        return Bounds(lower=lower, upper=upper)
    except ValueError:
        pass
    return InvalidBounds(lower=lower, upper=upper)


def bounds_set_from_proto(
    messages: Sequence[bounds_pb2.Bounds],
) -> BoundsSet | InvalidBoundsSet:
    """Convert a sequence of bounds messages into a single bounds set.

    This is the multi-bound counterpart of
    [`bounds_from_proto2`][..bounds_from_proto2]: it converts each message and
    combines the results.

    Args:
        messages: The bounds messages to convert.

    Returns:
        A [`BoundsSet`][....BoundsSet] (the union of the bounds) when every
            message is well-formed, or an
            [`InvalidBoundsSet`][....InvalidBoundsSet] preserving all the raw
            bounds in order when any message is malformed.
    """
    valid: list[Bounds] = []
    raw: list[Bounds | InvalidBounds] = []
    has_invalid = False
    for pb_bound in messages:
        match bounds_from_proto2(pb_bound):
            case Bounds() as bound:
                valid.append(bound)
                raw.append(bound)
            case InvalidBounds() as bound:
                has_invalid = True
                raw.append(bound)
            case unknown:
                assert_never(unknown)

    if has_invalid:
        return InvalidBoundsSet(bounds=tuple(raw))
    return BoundsSet(bounds=tuple(valid))


@deprecated(
    "frequenz.client.common.metrics.proto.v1alpha8.bounds_from_proto_with_issues "
    "is deprecated since v0.4.1. Use "
    "[frequenz.client.common.metrics.proto.v1alpha8.bounds_from_proto2][] instead."
)
def bounds_from_proto_with_issues(
    message: bounds_pb2.Bounds,
    *,
    major_issues: list[str],
    minor_issues: list[str],  # pylint: disable=unused-argument
) -> Bounds | None:  # noqa: DOC502
    """Create a [`Bounds`][....Bounds] object from a protobuf message, collecting issues.

    [`bounds_from_proto2`][..bounds_from_proto2] distinguishes well-formed from
    malformed data at the type level (`Bounds | InvalidBounds`) rather than
    routing invalid data through a side-channel string list.

    Args:
        message: The protobuf message to convert.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The corresponding [`Bounds`][....Bounds] object.
    """
    try:
        return Bounds(
            lower=message.lower if message.HasField("lower") else None,
            upper=message.upper if message.HasField("upper") else None,
        )
    except ValueError as exc:
        major_issues.append(str(exc))
        return None
