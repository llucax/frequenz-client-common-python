# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of PaginationInfo from/to protobuf v1alpha8."""

from frequenz.api.common.v1alpha8.pagination.pagination_info_pb2 import (
    PaginationInfo as PaginationInfoPb,
)
from typing_extensions import deprecated

from ....pagination import InvalidPaginationInfo, PaginationInfo


@deprecated(
    "frequenz.client.common.pagination.proto.v1alpha8.pagination_info_from_proto "
    "is deprecated since v0.4.1. Use "
    "[frequenz.client.common.pagination.proto.v1alpha8.pagination_info_from_proto2][] "
    "instead."
)
def pagination_info_from_proto(  # noqa: DOC502
    message: PaginationInfoPb,
) -> PaginationInfo:
    """Convert a protobuf message to a [`PaginationInfo`][....PaginationInfo] object.

    [`pagination_info_from_proto2`][..pagination_info_from_proto2] distinguishes
    well-formed from malformed data at the type level
    (`PaginationInfo | InvalidPaginationInfo`) rather than raising a
    `ValueError` when the invariant fires.

    Args:
        message: The protobuf message to convert.

    Returns:
        The corresponding [`PaginationInfo`][....PaginationInfo] object.

    Raises:
        ValueError: If the message carries a negative `total_items`.
    """
    return PaginationInfo(
        total_items=message.total_items,
        next_page_token=message.next_page_token if message.next_page_token else None,
    )


def pagination_info_from_proto2(
    message: PaginationInfoPb,
) -> PaginationInfo | InvalidPaginationInfo:
    """Convert a protobuf message to pagination information, preserving malformed data.

    Unlike [`pagination_info_from_proto`][..pagination_info_from_proto], the
    token is read through
    [`HasField()`][google.protobuf.message.Message.HasField], so a token the
    server actually sent is preserved even when it is empty; only an unset
    token becomes `None`.

    Args:
        message: The protobuf message to convert.

    Returns:
        A [`PaginationInfo`][....PaginationInfo] when the wire data is
            well-formed, or an
            [`InvalidPaginationInfo`][....InvalidPaginationInfo] preserving a
            `total_items` count that violates `total_items >= 0`.
    """
    next_page_token = (
        message.next_page_token if message.HasField("next_page_token") else None
    )
    try:
        return PaginationInfo(
            total_items=message.total_items, next_page_token=next_page_token
        )
    except ValueError:
        pass
    return InvalidPaginationInfo(
        total_items=message.total_items, next_page_token=next_page_token
    )


def pagination_info_to_proto(info: PaginationInfo) -> PaginationInfoPb:
    """Convert a [`PaginationInfo`][....PaginationInfo] object to a protobuf message.

    Args:
        info: The [`PaginationInfo`][....PaginationInfo] object to convert.

    Returns:
        The corresponding protobuf message.
    """
    return PaginationInfoPb(
        total_items=info.total_items,
        next_page_token=info.next_page_token,
    )
