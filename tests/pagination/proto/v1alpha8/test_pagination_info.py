# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for pagination info protobuf v1alpha8 conversions."""

from typing import cast

import pytest
from frequenz.api.common.v1alpha8.pagination import pagination_info_pb2

from frequenz.client.common.pagination import InvalidPaginationInfo, PaginationInfo
from frequenz.client.common.pagination.proto.v1alpha8 import (
    pagination_info_from_proto,
    pagination_info_from_proto2,
    pagination_info_to_proto,
)


def test_from_proto_with_token() -> None:
    """Test converting a protobuf PaginationInfo with a token."""
    proto = pagination_info_pb2.PaginationInfo(total_items=100, next_page_token="token")
    with pytest.deprecated_call(match="pagination_info_from_proto2"):
        info = pagination_info_from_proto(proto)
    assert info.total_items == 100
    assert info.next_page_token == "token"


def test_from_proto_empty_token() -> None:
    """Test converting an empty protobuf token to None."""
    proto = pagination_info_pb2.PaginationInfo(total_items=100, next_page_token="")
    with pytest.deprecated_call(match="pagination_info_from_proto2"):
        info = pagination_info_from_proto(proto)
    assert info.total_items == 100
    assert info.next_page_token is None


def test_from_proto_emits_deprecation_warning() -> None:
    """`pagination_info_from_proto` itself is deprecated and warns on call."""
    proto = pagination_info_pb2.PaginationInfo(total_items=1)
    with pytest.deprecated_call(
        match=r"^frequenz\.client\.common\.pagination\.proto\.v1alpha8\."
        r"pagination_info_from_proto is deprecated since v0\.4\.1\. Use "
        r"\[frequenz\.client\.common\.pagination\.proto\.v1alpha8\."
        r"pagination_info_from_proto2\]\[\] instead\.$"
    ):
        pagination_info_from_proto(proto)


def test_to_proto_with_token() -> None:
    """Test converting a PaginationInfo with a token to protobuf."""
    info = PaginationInfo(total_items=100, next_page_token="token")
    proto = pagination_info_to_proto(info)
    assert proto.total_items == 100
    assert proto.next_page_token == "token"


def test_roundtrip() -> None:
    """Test round-tripping PaginationInfo to protobuf and back."""
    info = PaginationInfo(total_items=100, next_page_token="token")
    proto = pagination_info_to_proto(info)
    roundtripped_info = pagination_info_from_proto2(proto)
    assert roundtripped_info == info


def test_from_proto2_with_token() -> None:
    """A well-formed message with a token becomes a `PaginationInfo`."""
    proto = pagination_info_pb2.PaginationInfo(total_items=100, next_page_token="token")
    info = pagination_info_from_proto2(proto)
    assert isinstance(info, PaginationInfo)
    assert info.total_items == 100
    assert info.next_page_token == "token"


def test_from_proto2_unset_token() -> None:
    """An unset token becomes `None`."""
    proto = pagination_info_pb2.PaginationInfo(total_items=100)
    info = pagination_info_from_proto2(proto)
    assert isinstance(info, PaginationInfo)
    assert info.total_items == 100
    assert info.next_page_token is None


def test_from_proto2_keeps_explicitly_empty_token() -> None:
    """A token the server sent is kept even when it is empty."""
    proto = pagination_info_pb2.PaginationInfo(total_items=100, next_page_token="")
    info = pagination_info_from_proto2(proto)
    assert isinstance(info, PaginationInfo)
    assert info.next_page_token == ""


def test_from_proto2_zero_total_items() -> None:
    """A zero count is well-formed."""
    info = pagination_info_from_proto2(pagination_info_pb2.PaginationInfo())
    assert isinstance(info, PaginationInfo)
    assert info.total_items == 0


class _NegativeTotalItemsPb:
    """A message-like object whose `total_items` is negative.

    The `total_items` field is a protobuf `uint32`, so a decoded message can
    never carry a negative count. This stand-in exercises the invalid branch
    of the converter, which must not raise regardless of what it is handed.
    """

    total_items = -1
    next_page_token = ""

    # pylint: disable-next=invalid-name,unused-argument
    def HasField(self, field_name: str) -> bool:
        """Report every field as unset.

        Args:
            field_name: The name of the field to check.

        Returns:
            Always `False`.
        """
        return False


def test_from_proto2_negative_total_items() -> None:
    """A negative count becomes an `InvalidPaginationInfo` instead of raising."""
    proto = cast(pagination_info_pb2.PaginationInfo, _NegativeTotalItemsPb())
    info = pagination_info_from_proto2(proto)
    assert isinstance(info, InvalidPaginationInfo)
    assert info.total_items == -1
    assert info.next_page_token is None
    assert str(info) == "items=<invalid:-1>,next=None"
