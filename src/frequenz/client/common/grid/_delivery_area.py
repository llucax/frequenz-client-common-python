# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Delivery area information for the energy market."""

import warnings
from dataclasses import InitVar, dataclass
from typing import Any, Self, assert_never

from frequenz.core.enum import Enum, deprecated_member, unique

from .._exception import (
    InvalidAttributeError,
    UnrecognizedEnumValueError,
    UnspecifiedEnumValueError,
)


@unique
class EnergyMarketCodeType(Enum):
    """The identification code types used in the energy market.

    CodeType specifies the type of identification code used for uniquely
    identifying various entities such as delivery areas, market participants,
    and grid components within the energy market.

    This enumeration aims to
    offer compatibility across different jurisdictional standards.

    Note: Understanding Code Types
        Different regions or countries may have their own standards for uniquely
        identifying various entities within the energy market. For example, in
        Europe, the Energy Identification Code (EIC) is commonly used for this
        purpose.

    Note: Extensibility
        New code types can be added to this enum to accommodate additional regional
        standards, enhancing the API's adaptability.

    Danger: Validation Required
        The chosen code type should correspond correctly with the `code` field in
        the relevant message objects, such as `DeliveryArea` or `Counterparty`.
        Failure to match the code type with the correct code could lead to
        processing errors.
    """

    UNSPECIFIED = deprecated_member(
        0,
        "frequenz.client.common.grid.EnergyMarketCodeType.UNSPECIFIED is "
        "deprecated since v0.4.1. Use the int value 0 instead if you really "
        "need to check for this low-level value.",
    )
    """Unspecified type. This value is a placeholder and should not be used."""

    EUROPE_EIC = 1
    """European Energy Identification Code Standard."""

    US_NERC = 2
    """North American Electric Reliability Corporation identifiers."""


@dataclass(frozen=True, kw_only=True)
class BaseDeliveryArea:
    """A base class for all delivery areas.

    This is the common supertype of both well-formed
    [`DeliveryArea`][..DeliveryArea] instances and
    [`InvalidDeliveryArea`][..InvalidDeliveryArea] instances that carry
    malformed wire data. It cannot be instantiated directly; use one of
    its concrete subclasses instead.
    """

    code: str | None
    """The code representing the unique identifier for the delivery area.

    Deprecated:
        Passing `None` is deprecated since v0.4.1. This field is required for a
        well-formed `DeliveryArea`, so we are making this more explicit by
        deprecating the use of `None` here. In the future, `| None` will be
        removed so passing `None` will fail type checking.
    """

    code_type: EnergyMarketCodeType | int
    """Type of code used for identifying the delivery area itself.

    This code could be extended in the future, in case an unknown code type is
    encountered, a plain integer value is used to represent it.

    Tip:
        This is the lower-level accessor; when working with a valid
        [`DeliveryArea`][...DeliveryArea], prefer
        [`get_code_type`][...DeliveryArea.get_code_type] to obtain a known
        member or a clear error.
    """

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is BaseDeliveryArea:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)

    def __post_init__(self) -> None:
        """Warn if this instance carries invalid data."""
        if self.code is None:
            warnings.warn(
                "Using `None` for `code` is deprecated and will be "
                "removed in a future release.",
                DeprecationWarning,
                stacklevel=3,
            )


@dataclass(frozen=True, kw_only=True)
class DeliveryArea(BaseDeliveryArea):
    """A geographical or administrative region where electricity deliveries occur.

    DeliveryArea represents the geographical or administrative region, usually defined
    and maintained by a Transmission System Operator (TSO), where electricity deliveries
    for a contract occur.

    The concept is important to energy trading as it delineates the agreed-upon delivery
    location. Delivery areas can have different codes based on the jurisdiction in
    which they operate.

    Deprecated:
        Constructing a `DeliveryArea` with invalid data is deprecated since
        v0.4.1, and will raise a [`ValueError`][] in a future release. The type
        itself is not deprecated. A well-formed `DeliveryArea` carries a
        non-empty [`code`][.code] and a specified [`code_type`][.code_type].

        You can temporarily use the `_raise_on_invalid` keyword argument to get
        the upcoming behavior now (raising instead of deprecation warning).

        Use [`InvalidDeliveryArea`][..InvalidDeliveryArea] if you need to
        represent a malformed message.

    Note: Jurisdictional Differences
        This is typically represented by specific codes according to local jurisdiction.

        In Europe, this is represented by an
        [EIC](https://en.wikipedia.org/wiki/Energy_Identification_Code) (Energy
        Identification Code). [List of
        EICs](https://www.entsoe.eu/data/energy-identification-codes-eic/eic-approved-codes/).
    """

    _raise_on_invalid: InitVar[bool] = False
    """Whether to raise a `ValueError` on invalid data.

    This will be removed in a future release and always raise on invalid data.
    """

    # pylint: disable-next=arguments-differ
    def __post_init__(self, _raise_on_invalid: bool) -> None:
        """Warn if this instance carries invalid data."""
        if not self.code:
            if _raise_on_invalid:
                raise ValueError("`code` cannot be None or empty")
            warnings.warn(
                "Constructing a DeliveryArea without a `code` is deprecated and will raise "
                "a `ValueError` in a future release. Use `InvalidDeliveryArea` instead.",
                DeprecationWarning,
                stacklevel=3,
            )
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            unspecified_code_type = EnergyMarketCodeType.UNSPECIFIED
        if self.code_type in (0, unspecified_code_type):
            if _raise_on_invalid:
                raise ValueError("`code_type` cannot be 0 (UNSPECIFIED)")
            warnings.warn(
                "Constructing a DeliveryArea with `code_type=0` is deprecated and will raise "
                "a `ValueError` in a future release. Use `InvalidDeliveryArea` instead.",
                DeprecationWarning,
                stacklevel=3,
            )

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        code_type = (
            f"type={self.code_type}"
            if isinstance(self.code_type, int)
            else self.code_type.name
        )
        return f"{self.code}[{code_type}]"

    def get_code_type(self) -> EnergyMarketCodeType:
        """Return the code type as a known enum member.

        This is the higher-level accessor for the `code_type` attribute: it
        resolves the value to a known `EnergyMarketCodeType` member or raises a
        clear, catchable error.

        Returns:
            The code type, when it is a known `EnergyMarketCodeType` member.

        Raises:
            UnspecifiedEnumValueError: If the code type is unspecified.
            UnrecognizedEnumValueError: If the code type is a value not
                recognized by this version of the client. The raw value is
                available on the exception's `value` attribute.
        """
        # Suppressing the deprecation warning can be removed when UNSPECIFIED is removed
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            match self.code_type:
                case 0 | EnergyMarketCodeType.UNSPECIFIED:
                    raise UnspecifiedEnumValueError(self, "code_type")
                case EnergyMarketCodeType() as code_type:
                    return code_type
                case int() as code_type:
                    raise UnrecognizedEnumValueError(self, "code_type", code_type)
                case unknown:
                    assert_never(unknown)


@dataclass(frozen=True, kw_only=True)
class InvalidDeliveryArea(BaseDeliveryArea):
    """A delivery area with malformed data received from the wire.

    Represents delivery area data that fails the invariants required for a
    well-formed [`DeliveryArea`][..DeliveryArea]. Callers can inspect the raw
    fields to recover partial information.

    This class does not enforce any invariants on construction.
    """

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        # Suppressing the deprecation warning can be removed when UNSPECIFIED
        # is removed
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            match self.code_type:
                case 0 | EnergyMarketCodeType.UNSPECIFIED:
                    code_type = "type=<invalid:0>"
                case EnergyMarketCodeType() as enum_code:
                    code_type = enum_code.name
                case int() as int_code:
                    code_type = f"type={int_code}"
                case unexpected:
                    assert_never(unexpected)
        code = self.code or f"<invalid:{self.code!r}>"
        return f"{code}[{code_type}]"


class InvalidDeliveryAreaError(InvalidAttributeError):
    """Raised when a semantic accessor sees an invalid delivery area.

    The offending [`InvalidDeliveryArea`][..InvalidDeliveryArea] instance
    is available as the `delivery_area` attribute so callers can inspect
    the raw wire data.

    This is also a [`ValueError`][] for convenience.
    """

    def __init__(
        self,
        instance: object,
        attr_name: str,
        delivery_area: InvalidDeliveryArea,
        message: str | None = None,
    ) -> None:
        """Initialize this error.

        Args:
            instance: The instance that was being accessed when this error was raised.
            attr_name: The name of the attribute that was being accessed when this
                error was raised.
            delivery_area: The invalid delivery area instance.
            message: A custom error message. If `None`, a default message
                mentioning the invalid delivery area is used.
        """
        self.delivery_area: InvalidDeliveryArea = delivery_area
        """The invalid delivery area instance that caused this error."""

        message = (
            f"invalid delivery area {delivery_area} for attribute {attr_name!r} in {instance}"
            if message is None
            else message
        )
        super().__init__(instance, attr_name, message)
