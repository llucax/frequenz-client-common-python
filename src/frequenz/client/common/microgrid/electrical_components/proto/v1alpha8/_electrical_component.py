# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of electrical components to/from protobuf v1alpha8."""

from collections.abc import Mapping, Sequence
from typing import Final, NamedTuple, TypeAlias, assert_never, overload

from frequenz.api.common.v1alpha8.metrics import bounds_pb2
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.core.warnings import ignoring_deprecations
from google.protobuf.json_format import MessageToDict

from .....metrics import BoundsSet, InvalidBoundsSet, Metric
from .....metrics.proto.v1alpha8._bounds import bounds_set_from_proto
from .....proto import enum_from_proto
from ...._ids import MicrogridId
from ...._lifetime import InvalidLifetime, Lifetime
from ....proto.v1alpha8 import lifetime_from_proto
from ..._battery import (
    Battery,
    LiIonBattery,
    NaIonBattery,
    UnrecognizedBattery,
    UnspecifiedBattery,
)
from ..._breaker import Breaker
from ..._capacitor_bank import CapacitorBank
from ..._category import ElectricalComponentCategory
from ..._category_specific_info import CategorySpecificInfo
from ..._chp import Chp
from ..._converter import Converter
from ..._crypto_miner import CryptoMiner
from ..._electrical_component import ElectricalComponent
from ..._electrolyzer import Electrolyzer
from ..._ev_charger import (
    AcEvCharger,
    DcEvCharger,
    EvCharger,
    HybridEvCharger,
    UnrecognizedEvCharger,
    UnspecifiedEvCharger,
)
from ..._grid_connection_point import GridConnectionPoint
from ..._hvac import Hvac
from ..._ids import ElectricalComponentId
from ..._inverter import (
    BatteryInverter,
    HybridInverter,
    Inverter,
    PvInverter,
    UnrecognizedInverter,
    UnspecifiedInverter,
)
from ..._meter import Meter
from ..._plc import Plc
from ..._power_transformer import PowerTransformer
from ..._precharger import Precharger
from ..._problematic import (
    MismatchedCategoryElectricalComponent,
    UnrecognizedElectricalComponent,
    UnspecifiedElectricalComponent,
)
from ..._static_transfer_switch import StaticTransferSwitch
from ..._steam_boiler import SteamBoiler
from ..._types import ElectricalComponentTypes
from ..._uninterruptible_power_supply import UninterruptiblePowerSupply
from ..._wind_turbine import WindTurbine

# We disable `too-many-arguments` in the whole file because all `_from_proto` functions
# are expected to take many arguments, and `too-many-lines` because this module bundles
# the class-level and message-level converters (which share lookup tables).
# pylint: disable=too-many-arguments,too-many-lines


# ============================================================================
# Type aliases
# ============================================================================

ProtoTypeEnums: TypeAlias = (
    electrical_components_pb2.BatteryType.ValueType
    | electrical_components_pb2.EvChargerType.ValueType
    | electrical_components_pb2.InverterType.ValueType
)
"""Type alias for all protobuf type enums for electrical components."""

AbstractTypedTypes: TypeAlias = Battery | EvCharger | Inverter
"""Type alias for all abstract electrical component classes that have a type enum."""

SpecifiedConcreteTypelessTypes: TypeAlias = (
    Breaker
    | CapacitorBank
    | Chp
    | Converter
    | CryptoMiner
    | Electrolyzer
    | GridConnectionPoint
    | Hvac
    | Meter
    | Plc
    | PowerTransformer
    | Precharger
    | StaticTransferSwitch
    | SteamBoiler
    | UninterruptiblePowerSupply
    | WindTurbine
)
"""Type alias for all specified concrete electrical component classes without a type enum."""

ConcreteTypelessTypes: TypeAlias = (
    SpecifiedConcreteTypelessTypes | UnspecifiedElectricalComponent
)
"""Type alias for all concrete electrical component classes that don't have a type enum."""

ConcreteTypedTypes: TypeAlias = (
    LiIonBattery
    | NaIonBattery
    | UnspecifiedBattery
    | AcEvCharger
    | DcEvCharger
    | HybridEvCharger
    | UnspecifiedEvCharger
    | BatteryInverter
    | PvInverter
    | HybridInverter
    | UnspecifiedInverter
)
"""Type alias for all concrete electrical component classes that have a type enum."""

ConvertibleElectricalComponentTypes: TypeAlias = (
    ConcreteTypedTypes | AbstractTypedTypes | ConcreteTypelessTypes
)
"""Type alias for all classes that can be converted to protobuf category/subtype pairs."""


# ============================================================================
# Shared class ↔ protobuf identity tables
# ============================================================================

_PROTO_CATEGORY_BY_TYPELESS_CLASS: Final[
    Mapping[
        type[
            AbstractTypedTypes
            | ConcreteTypelessTypes
            | UnrecognizedBattery
            | UnrecognizedEvCharger
            | UnrecognizedInverter
        ],
        electrical_components_pb2.ElectricalComponentCategory.ValueType,
    ]
] = {
    Battery: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
    Breaker: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BREAKER,
    CapacitorBank: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CAPACITOR_BANK
    ),
    Chp: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CHP,
    Converter: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CONVERTER,
    CryptoMiner: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CRYPTO_MINER,
    Electrolyzer: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_ELECTROLYZER,
    EvCharger: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
    GridConnectionPoint: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT
    ),
    Hvac: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_HVAC,
    Inverter: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
    Meter: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_METER,
    Plc: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PLC,
    PowerTransformer: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_POWER_TRANSFORMER
    ),
    Precharger: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PRECHARGER,
    StaticTransferSwitch: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STATIC_TRANSFER_SWITCH
    ),
    SteamBoiler: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STEAM_BOILER,
    UninterruptiblePowerSupply: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNINTERRUPTIBLE_POWER_SUPPLY
    ),
    UnrecognizedBattery: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY
    ),
    UnrecognizedEvCharger: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER
    ),
    UnrecognizedInverter: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER
    ),
    UnspecifiedElectricalComponent: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED
    ),
    WindTurbine: electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_WIND_TURBINE,
}
"""Class → protobuf category for components whose protobuf identity has no subtype.

This covers four kinds of class:

* Truly typeless concrete classes (`Breaker`, `Meter`, ..., `WindTurbine`,
  `GridConnectionPoint`, `PowerTransformer`).
* The unspecified top-level marker `UnspecifiedElectricalComponent`.
* The abstract typed bases `Battery`, `EvCharger` and `Inverter` — when
  converted to protobuf these emit `subtype=None` to mark "category known,
  subtype not".
* The per-family unrecognized classes `UnrecognizedBattery`,
  `UnrecognizedEvCharger`, `UnrecognizedInverter` when passed as classes. (As
  instances, they carry the raw subtype int and are handled specially in
  `electrical_component_class_to_proto`.)
"""

_PROTO_CATEGORY_TYPE_BY_TYPED_CLASS: Final[
    Mapping[
        type[ConcreteTypedTypes],
        tuple[
            electrical_components_pb2.ElectricalComponentCategory.ValueType,
            ProtoTypeEnums,
        ],
    ]
] = {
    UnspecifiedBattery: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
        electrical_components_pb2.BATTERY_TYPE_UNSPECIFIED,
    ),
    LiIonBattery: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
        electrical_components_pb2.BATTERY_TYPE_LI_ION,
    ),
    NaIonBattery: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
        electrical_components_pb2.BATTERY_TYPE_NA_ION,
    ),
    UnspecifiedEvCharger: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
        electrical_components_pb2.EV_CHARGER_TYPE_UNSPECIFIED,
    ),
    AcEvCharger: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
        electrical_components_pb2.EV_CHARGER_TYPE_AC,
    ),
    DcEvCharger: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
        electrical_components_pb2.EV_CHARGER_TYPE_DC,
    ),
    HybridEvCharger: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
        electrical_components_pb2.EV_CHARGER_TYPE_HYBRID,
    ),
    UnspecifiedInverter: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
        electrical_components_pb2.INVERTER_TYPE_UNSPECIFIED,
    ),
    BatteryInverter: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
        electrical_components_pb2.INVERTER_TYPE_BATTERY,
    ),
    PvInverter: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
        electrical_components_pb2.INVERTER_TYPE_PV,
    ),
    HybridInverter: (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
        electrical_components_pb2.INVERTER_TYPE_HYBRID,
    ),
}
"""Concrete typed class → `(category, subtype)` pair.

Only carries the well-formed concrete classes (no abstract bases, no
`Unrecognized*` families): unspecified and unrecognized cases are surfaced
through neighbouring tables instead.
"""

_PROTO_BY_CLASS: Final[
    Mapping[
        type[
            ConcreteTypedTypes
            | AbstractTypedTypes
            | ConcreteTypelessTypes
            | UnrecognizedBattery
            | UnrecognizedEvCharger
            | UnrecognizedInverter
        ],
        tuple[
            electrical_components_pb2.ElectricalComponentCategory.ValueType,
            ProtoTypeEnums | None,
        ],
    ]
] = {
    **{cls: (cat, None) for cls, cat in _PROTO_CATEGORY_BY_TYPELESS_CLASS.items()},
    **{
        cls: (cat, sub)
        for cls, (cat, sub) in _PROTO_CATEGORY_TYPE_BY_TYPED_CLASS.items()
    },
}
"""Combined class → `(category, subtype | None)` lookup used by `_class_to_proto`."""


_BATTERY_CLASS_BY_PROTO_TYPE: Final[
    Mapping[
        electrical_components_pb2.BatteryType.ValueType,
        type[UnspecifiedBattery | LiIonBattery | NaIonBattery],
    ]
] = {
    electrical_components_pb2.BATTERY_TYPE_UNSPECIFIED: UnspecifiedBattery,
    electrical_components_pb2.BATTERY_TYPE_LI_ION: LiIonBattery,
    electrical_components_pb2.BATTERY_TYPE_NA_ION: NaIonBattery,
}
"""Battery subtype → concrete battery class (`Unrecognized*` is the fallback)."""

_EV_CHARGER_CLASS_BY_PROTO_TYPE: Final[
    Mapping[
        electrical_components_pb2.EvChargerType.ValueType,
        type[UnspecifiedEvCharger | AcEvCharger | DcEvCharger | HybridEvCharger],
    ]
] = {
    electrical_components_pb2.EV_CHARGER_TYPE_UNSPECIFIED: UnspecifiedEvCharger,
    electrical_components_pb2.EV_CHARGER_TYPE_AC: AcEvCharger,
    electrical_components_pb2.EV_CHARGER_TYPE_DC: DcEvCharger,
    electrical_components_pb2.EV_CHARGER_TYPE_HYBRID: HybridEvCharger,
}
"""EV charger subtype → concrete EV charger class (`Unrecognized*` is the fallback)."""

_INVERTER_CLASS_BY_PROTO_TYPE: Final[
    Mapping[
        electrical_components_pb2.InverterType.ValueType,
        type[UnspecifiedInverter | BatteryInverter | PvInverter | HybridInverter],
    ]
] = {
    electrical_components_pb2.INVERTER_TYPE_UNSPECIFIED: UnspecifiedInverter,
    electrical_components_pb2.INVERTER_TYPE_BATTERY: BatteryInverter,
    electrical_components_pb2.INVERTER_TYPE_PV: PvInverter,
    electrical_components_pb2.INVERTER_TYPE_HYBRID: HybridInverter,
}
"""Inverter subtype → concrete inverter class (`Unrecognized*` is the fallback)."""

_TYPELESS_CLASS_BY_PROTO_CATEGORY: Final[
    Mapping[
        electrical_components_pb2.ElectricalComponentCategory.ValueType,
        type[ConcreteTypelessTypes],
    ]
] = {
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED: (
        UnspecifiedElectricalComponent
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BREAKER: Breaker,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CAPACITOR_BANK: (
        CapacitorBank
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CHP: Chp,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CONVERTER: Converter,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CRYPTO_MINER: CryptoMiner,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_ELECTROLYZER: Electrolyzer,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT: (
        GridConnectionPoint
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_HVAC: Hvac,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_METER: Meter,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PLC: Plc,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_POWER_TRANSFORMER: (
        PowerTransformer
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PRECHARGER: Precharger,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STATIC_TRANSFER_SWITCH: (
        StaticTransferSwitch
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STEAM_BOILER: SteamBoiler,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNINTERRUPTIBLE_POWER_SUPPLY: (
        UninterruptiblePowerSupply
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_WIND_TURBINE: WindTurbine,
}
"""Typeless category → concrete typeless class."""

_ABSTRACT_CLASS_BY_TYPED_PROTO_CATEGORY: Final[
    Mapping[
        electrical_components_pb2.ElectricalComponentCategory.ValueType,
        type[AbstractTypedTypes],
    ]
] = {
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY: Battery,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER: EvCharger,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER: Inverter,
}
"""Typed category → abstract base class (returned by `_class_from_proto` when subtype is `None`)."""

_UNRECOGNIZED_CLASS_BY_TYPED_PROTO_CATEGORY: Final[
    Mapping[
        electrical_components_pb2.ElectricalComponentCategory.ValueType,
        type[UnrecognizedBattery | UnrecognizedEvCharger | UnrecognizedInverter],
    ]
] = {
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY: UnrecognizedBattery,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER: (
        UnrecognizedEvCharger
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER: UnrecognizedInverter,
}
"""Typed category → per-family unrecognized fallback class."""

_TYPED_CLASS_BY_PROTO: Final[
    Mapping[
        tuple[
            electrical_components_pb2.ElectricalComponentCategory.ValueType,
            ProtoTypeEnums,
        ],
        type[ConcreteTypedTypes],
    ]
] = {proto_pair: cls for cls, proto_pair in _PROTO_CATEGORY_TYPE_BY_TYPED_CLASS.items()}
"""`(category, subtype)` → concrete typed class.

The inverse of `_PROTO_CATEGORY_TYPE_BY_TYPED_CLASS`.
"""

_TRIVIAL_TYPELESS_CLASS_BY_PROTO_CATEGORY: Final[
    Mapping[
        electrical_components_pb2.ElectricalComponentCategory.ValueType,
        type[
            UnspecifiedElectricalComponent
            | Breaker
            | CapacitorBank
            | Chp
            | Converter
            | CryptoMiner
            | Electrolyzer
            | Hvac
            | Meter
            | Plc
            | Precharger
            | StaticTransferSwitch
            | SteamBoiler
            | UninterruptiblePowerSupply
            | WindTurbine
        ],
    ]
] = {
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED: (
        UnspecifiedElectricalComponent
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BREAKER: Breaker,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CAPACITOR_BANK: (
        CapacitorBank
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CHP: Chp,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CONVERTER: Converter,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CRYPTO_MINER: CryptoMiner,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_ELECTROLYZER: Electrolyzer,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_HVAC: Hvac,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_METER: Meter,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PLC: Plc,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PRECHARGER: Precharger,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STATIC_TRANSFER_SWITCH: (
        StaticTransferSwitch
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STEAM_BOILER: SteamBoiler,
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNINTERRUPTIBLE_POWER_SUPPLY: (
        UninterruptiblePowerSupply
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_WIND_TURBINE: WindTurbine,
}
"""The subset of `_TYPELESS_CLASS_BY_PROTO_CATEGORY` whose classes need no extra args."""


# ============================================================================
# Class converters
# ============================================================================


# --- Battery overloads ------------------------------------------------------
@overload
def electrical_component_class_to_proto(
    component: (
        LiIonBattery
        | NaIonBattery
        | UnspecifiedBattery
        | type[LiIonBattery | NaIonBattery | UnspecifiedBattery]
    ),
) -> tuple[
    electrical_components_pb2.ElectricalComponentCategory.ValueType,
    electrical_components_pb2.BatteryType.ValueType,
]: ...


@overload
def electrical_component_class_to_proto(
    component: UnrecognizedBattery,
) -> tuple[electrical_components_pb2.ElectricalComponentCategory.ValueType, int]: ...


@overload
def electrical_component_class_to_proto(
    component: type[Battery],
) -> tuple[
    electrical_components_pb2.ElectricalComponentCategory.ValueType,
    electrical_components_pb2.BatteryType.ValueType | None,
]: ...


# --- EV charger overloads ---------------------------------------------------
@overload
def electrical_component_class_to_proto(
    component: (
        AcEvCharger
        | DcEvCharger
        | HybridEvCharger
        | UnspecifiedEvCharger
        | type[AcEvCharger | DcEvCharger | HybridEvCharger | UnspecifiedEvCharger]
    ),
) -> tuple[
    electrical_components_pb2.ElectricalComponentCategory.ValueType,
    electrical_components_pb2.EvChargerType.ValueType,
]: ...


@overload
def electrical_component_class_to_proto(
    component: UnrecognizedEvCharger,
) -> tuple[electrical_components_pb2.ElectricalComponentCategory.ValueType, int]: ...


@overload
def electrical_component_class_to_proto(
    component: type[EvCharger],
) -> tuple[
    electrical_components_pb2.ElectricalComponentCategory.ValueType,
    electrical_components_pb2.EvChargerType.ValueType | None,
]: ...


# --- Inverter overloads -----------------------------------------------------
@overload
def electrical_component_class_to_proto(
    component: (
        BatteryInverter
        | PvInverter
        | HybridInverter
        | UnspecifiedInverter
        | type[BatteryInverter | PvInverter | HybridInverter | UnspecifiedInverter]
    ),
) -> tuple[
    electrical_components_pb2.ElectricalComponentCategory.ValueType,
    electrical_components_pb2.InverterType.ValueType,
]: ...


@overload
def electrical_component_class_to_proto(
    component: UnrecognizedInverter,
) -> tuple[electrical_components_pb2.ElectricalComponentCategory.ValueType, int]: ...


@overload
def electrical_component_class_to_proto(
    component: type[Inverter],
) -> tuple[
    electrical_components_pb2.ElectricalComponentCategory.ValueType,
    electrical_components_pb2.InverterType.ValueType | None,
]: ...


# --- Typeless overloads -----------------------------------------------------
@overload
def electrical_component_class_to_proto(
    component: ConcreteTypelessTypes | type[ConcreteTypelessTypes],
) -> tuple[electrical_components_pb2.ElectricalComponentCategory.ValueType, None]: ...


# --- Problematic top-level overloads ----------------------------------------
@overload
def electrical_component_class_to_proto(
    component: UnrecognizedElectricalComponent,
) -> tuple[int, None]: ...


@overload
def electrical_component_class_to_proto(
    component: MismatchedCategoryElectricalComponent,
) -> tuple[int, None]: ...


def electrical_component_class_to_proto(
    component: ElectricalComponentTypes | type[ConvertibleElectricalComponentTypes],
) -> tuple[
    electrical_components_pb2.ElectricalComponentCategory.ValueType | int,
    ProtoTypeEnums | int | None,
]:
    """Convert an electrical component class or instance to its protobuf identity.

    Returns the `(category, subtype)` pair the protobuf wire format uses for
    the given component. This is the inverse of
    [`electrical_component_class_from_proto`][..electrical_component_class_from_proto]
    for the classes and abstract bases it knows about.

    Conversion rules (`C` = class, `I` = instance):

    * `LiIonBattery` / `NaIonBattery` / `UnspecifiedBattery` (`C` or `I`)
      → `(BATTERY, <matching BATTERY_TYPE_*>)`.
    * `UnrecognizedBattery` **instance**
      → `(BATTERY, instance.type)` — preserves the raw int.
    * `AcEvCharger` / `DcEvCharger` / `HybridEvCharger` / `UnspecifiedEvCharger`
      (`C` or `I`) → `(EV_CHARGER, <matching EV_CHARGER_TYPE_*>)`.
    * `UnrecognizedEvCharger` **instance**
      → `(EV_CHARGER, instance.type)`.
    * `BatteryInverter` / `PvInverter` / `HybridInverter` / `UnspecifiedInverter`
      (`C` or `I`) → `(INVERTER, <matching INVERTER_TYPE_*>)`.
    * `UnrecognizedInverter` **instance**
      → `(INVERTER, instance.type)`.
    * The abstract bases `Battery` / `EvCharger` / `Inverter` (class only)
      → `( <that category>, None)`.
    * Any concrete typeless class — `Breaker`, `CapacitorBank`, ...,
      `WindTurbine`, `GridConnectionPoint`, `PowerTransformer` — (`C` or `I`)
      → `( <that category>, None)`.
    * `UnspecifiedElectricalComponent` (`C` or `I`)
      → `(UNSPECIFIED, None)`.
    * `UnrecognizedElectricalComponent` **instance**
      → `(instance.category, None)` — preserves the raw int.
    * `MismatchedCategoryElectricalComponent` **instance**
      → `(instance.category, None)`.
    * The per-family `UnrecognizedBattery` / `UnrecognizedEvCharger` /
      `UnrecognizedInverter` (class only) → `( <that family's category>, None)`
      (the raw int is unavailable).

    Key invariants:

    * The abstract typed bases `Battery`, `EvCharger`, `Inverter` are
      *distinct* from their `Unspecified*` counterparts on the wire: abstract
      bases emit `subtype=None`, the `Unspecified*` classes emit
      `subtype=<...TYPE_UNSPECIFIED>` (the concrete protobuf 0 value). This
      mirrors how
      [`electrical_component_class_from_proto`][..electrical_component_class_from_proto]
      reads them back.
    * `Unrecognized*` and `MismatchedCategoryElectricalComponent` are only
      meaningful as **instances** because the raw, possibly out-of-range
      category or subtype int lives on the instance. Passing the per-family
      `UnrecognizedBattery`/`UnrecognizedEvCharger`/`UnrecognizedInverter` as
      classes still succeeds (returning `(category, None)`), but the raw int
      is unavailable. Passing the top-level
      `UnrecognizedElectricalComponent` or `MismatchedCategoryElectricalComponent`
      as classes raises `TypeError` because no category is recoverable.

    Note:
        Due to the way `mypy` resolves overloads, passing one of the abstract
        typed bases (e.g. `Battery`) returns the static type
        `tuple[category, <subtype-enum> | None]`: at runtime the subtype is
        always `None`. Callers that already know they are passing an abstract
        base usually just discard the subtype.

    Args:
        component: An electrical component class or instance to encode.

    Returns:
        The `(category, subtype)` pair encoding `component`. The subtype is
            `None` for typeless categories and for the abstract typed bases.

    Raises:
        TypeError: If `component` is a class this converter does not know how
            to encode (e.g. `ElectricalComponent`, `ProblematicElectricalComponent`,
            `UnrecognizedElectricalComponent` or
            `MismatchedCategoryElectricalComponent` passed as classes — for
            the latter two the raw category int lives on the instance and is
            unrecoverable from the class alone).
    """
    unrecognized_subtype: int | None = None
    component_class: type[
        ConcreteTypedTypes
        | AbstractTypedTypes
        | ConcreteTypelessTypes
        | UnrecognizedBattery
        | UnrecognizedEvCharger
        | UnrecognizedInverter
    ]

    match component:
        case UnrecognizedElectricalComponent(category=category):
            return (category, None)
        case MismatchedCategoryElectricalComponent(category=category):
            return (category, None)
        case (
            UnrecognizedBattery(type=raw_subtype)
            | UnrecognizedEvCharger(type=raw_subtype)
            | UnrecognizedInverter(type=raw_subtype)
        ):
            component_class = type(component)
            unrecognized_subtype = raw_subtype
        case ElectricalComponent():
            component_class = type(component)
        case type() as klass:
            component_class = klass
        case unexpected_component:
            assert_never(unexpected_component)

    try:
        category, subtype = _PROTO_BY_CLASS[component_class]
    except KeyError as exc:
        raise TypeError(
            f"unsupported electrical component class: {component_class.__name__}"
        ) from exc

    return (category, unrecognized_subtype if subtype is None else subtype)


def electrical_component_class_from_proto(
    category: electrical_components_pb2.ElectricalComponentCategory.ValueType,
    subtype: ProtoTypeEnums | None = None,
) -> type[
    AbstractTypedTypes
    | ConcreteTypedTypes
    | ConcreteTypelessTypes
    | UnrecognizedBattery
    | UnrecognizedEvCharger
    | UnrecognizedInverter
    | UnrecognizedElectricalComponent
]:
    """Convert a protobuf `(category, subtype)` pair to an electrical component class.

    This is the inverse of
    [`electrical_component_class_to_proto`][..electrical_component_class_to_proto]:
    every input it can produce round-trips back to the matching class here.
    Returns the class only — never an instance — because the protobuf identity
    pair does not carry the rest of the component state.

    Conversion rules:

    * `(BATTERY, None)` → `Battery` (abstract).
    * `(BATTERY, BATTERY_TYPE_UNSPECIFIED)` → `UnspecifiedBattery`.
    * `(BATTERY, BATTERY_TYPE_LI_ION)` → `LiIonBattery`.
    * `(BATTERY, BATTERY_TYPE_NA_ION)` → `NaIonBattery`.
    * `(BATTERY, <unknown subtype int>)` → `UnrecognizedBattery`.
    * `(EV_CHARGER, None)` → `EvCharger` (abstract).
    * `(EV_CHARGER, EV_CHARGER_TYPE_UNSPECIFIED)` → `UnspecifiedEvCharger`.
    * `(EV_CHARGER, EV_CHARGER_TYPE_AC)` → `AcEvCharger`.
    * `(EV_CHARGER, EV_CHARGER_TYPE_DC)` → `DcEvCharger`.
    * `(EV_CHARGER, EV_CHARGER_TYPE_HYBRID)` → `HybridEvCharger`.
    * `(EV_CHARGER, <unknown subtype int>)` → `UnrecognizedEvCharger`.
    * `(INVERTER, None)` → `Inverter` (abstract).
    * `(INVERTER, INVERTER_TYPE_UNSPECIFIED)` → `UnspecifiedInverter`.
    * `(INVERTER, INVERTER_TYPE_BATTERY)` → `BatteryInverter`.
    * `(INVERTER, INVERTER_TYPE_PV)` → `PvInverter`.
    * `(INVERTER, INVERTER_TYPE_HYBRID)` → `HybridInverter`.
    * `(INVERTER, <unknown subtype int>)` → `UnrecognizedInverter`.
    * `(UNSPECIFIED, None)` → `UnspecifiedElectricalComponent`.
    * `(<any other typeless category>, None)` → its concrete typeless class
      (`Breaker`, `Meter`, ... one per category).
    * `(<any known typeless category>, <non-None subtype>)` → raises
      [`ValueError`][].
    * `(<unknown category int>, <any subtype>)` → `UnrecognizedElectricalComponent`
      (subtype silently dropped).

    Notes:
        * For typed categories the abstract base
          (`Battery`/`EvCharger`/`Inverter`) is returned only when
          `subtype is None`; passing the concrete `TYPE_UNSPECIFIED`
          int returns the corresponding `Unspecified*` class instead. This is
          the same distinction `electrical_component_class_to_proto` makes on
          the way out.
        * For known typeless categories any non-`None` subtype is an error
          because the protobuf wire format has no such combination.
        * For unknown categories the subtype is silently dropped — the integer
          category alone is enough to mark the component as unrecognized, and
          the caller passed the subtype in so they already have it.

    Args:
        category: A protobuf electrical component category value.
        subtype: A protobuf subtype value (`BatteryType`, `EvChargerType`
            or `InverterType` `.ValueType`), or `None` for typeless
            categories and abstract typed bases.

    Returns:
        The corresponding electrical component class.

    Raises:
        ValueError: If `subtype` is not `None` for a known typeless category —
            that combination has no representation in the protobuf wire format.
    """
    abstract_base = _ABSTRACT_CLASS_BY_TYPED_PROTO_CATEGORY.get(category)
    if abstract_base is not None:
        if subtype is None:
            return abstract_base
        typed_class = _TYPED_CLASS_BY_PROTO.get((category, subtype))
        if typed_class is not None:
            return typed_class
        return _UNRECOGNIZED_CLASS_BY_TYPED_PROTO_CATEGORY[category]

    typeless_class = _TYPELESS_CLASS_BY_PROTO_CATEGORY.get(category)
    if typeless_class is not None:
        if subtype is not None:
            raise ValueError(
                f"protobuf subtype {int(subtype)!r} is not valid for typeless "
                f"category {int(category)!r}"
            )
        return typeless_class

    return UnrecognizedElectricalComponent


# ============================================================================
# Message converters (full protobuf message ↔ instance)
# ============================================================================

_BOOLS_BY_OPERATIONAL_MODE: dict[int, tuple[bool, bool]] = {
    electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_INACTIVE: (
        False,
        False,
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_TELEMETRY_ONLY: (
        True,
        False,
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_CONTROL_ONLY: (
        False,
        True,
    ),
    electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_CONTROL_AND_TELEMETRY: (
        True,
        True,
    ),
}


def _operational_mode_to_bools(value: int) -> tuple[bool, bool] | tuple[int, int]:
    """Map a protobuf operational mode to telemetry/control booleans.

    Args:
        value: A protobuf operational-mode enum value (an
            `ELECTRICAL_COMPONENT_OPERATIONAL_MODE_*` constant).

    Returns:
        A `(provides_telemetry, accepts_control)` tuple of `bool`s for known
            operational modes, or `(value, value)` (the raw `int` `value`
            duplicated) when the operational mode is unspecified (`0`) or
            unrecognized. This forward-compatible representation lets the
            higher-level accessors distinguish unspecified from unrecognized
            values.
    """
    return _BOOLS_BY_OPERATIONAL_MODE.get(value, (value, value))


class _ElectricalComponentBaseData(NamedTuple):
    """Base data for an electrical component, extracted from a protobuf message."""

    component_id: ElectricalComponentId
    """The unique identifier of the electrical component."""

    microgrid_id: MicrogridId
    """The unique identifier of the parent microgrid."""

    name: str
    """The human-readable name of the electrical component."""

    model: str
    """The model string of the electrical component."""

    category: ElectricalComponentCategory | int
    """The category of the electrical component."""

    lifetime: Lifetime | InvalidLifetime
    """The operational lifetime of the electrical component."""

    metric_config_bounds: dict[Metric | int, BoundsSet | InvalidBoundsSet]
    """The metric configuration bounds extracted from the protobuf message.

    Each metric maps to the aggregate of every entry it had on the wire: a
    [`BoundsSet`][frequenz.client.common.metrics.BoundsSet] when all are
    well-formed, or an
    [`InvalidBoundsSet`][frequenz.client.common.metrics.InvalidBoundsSet]
    preserving all the raw bounds when any is malformed. A metric with no
    configured limits maps to the empty, unbounded
    [`BoundsSet`][frequenz.client.common.metrics.BoundsSet].
    """

    category_specific_info: CategorySpecificInfo | None
    """The category specific info extracted from the protobuf message, if any."""

    provides_telemetry: bool | int
    """Whether the electrical component provides telemetry, or `None` if unknown."""

    accepts_control: bool | int
    """Whether the electrical component accepts control, or `None` if unknown."""

    category_mismatched: bool = False
    """Whether the declared category and the carried info disagree."""


_CATEGORY_NAME_PREFIX = "ELECTRICAL_COMPONENT_CATEGORY_"


def _category_name(category: int) -> str | None:
    """Return the short protobuf enum name for a category, or `None` if unknown.

    Args:
        category: The raw protobuf category value.

    Returns:
        The protobuf enum name without its `ELECTRICAL_COMPONENT_CATEGORY_`
            prefix (e.g. `"BATTERY"`), or `None` when the value is not a known
            protobuf enum value.
    """
    proto_enum = electrical_components_pb2.ElectricalComponentCategory
    try:
        name = proto_enum.Name(proto_enum.ValueType(category))
    except ValueError:
        return None
    return name.removeprefix(_CATEGORY_NAME_PREFIX)


def _leftover_info(
    info: CategorySpecificInfo | None, *translated_keys: str
) -> CategorySpecificInfo | None:
    """Return the info without the fields translated into typed attributes.

    The variant `kind` is preserved whenever info was carried, so an empty
    result still records which variant the wire carried.

    Args:
        info: The full info carried on the wire, or `None` if none was.
        *translated_keys: The field names already translated into typed
            attributes on the target component.

    Returns:
        The info without `translated_keys`, or `None` if no info was carried.
    """
    if info is None:
        return None
    leftover = {
        key: value for key, value in info.fields.items() if key not in translated_keys
    }
    return CategorySpecificInfo(kind=info.kind, fields=leftover)


# pylint: disable-next=too-many-locals
def _electrical_component_base_from_proto(
    message: electrical_components_pb2.ElectricalComponent,
) -> _ElectricalComponentBaseData:
    """Extract base data from a protobuf message.

    Args:
        message: The protobuf message.

    Returns:
        An `_ElectricalComponentBaseData` named tuple containing the extracted data.
    """
    with ignoring_deprecations():
        component_id = ElectricalComponentId(message.id)
        microgrid_id = MicrogridId(message.microgrid_id)

        provides_telemetry, accepts_control = _operational_mode_to_bools(
            message.operational_mode
        )

        lifetime = _get_operational_lifetime_from_proto(message)

        metric_config_bounds = _metric_config_bounds_from_proto(
            message.metric_config_bounds
        )

        category = enum_from_proto(message.category, ElectricalComponentCategory)

        category_specific_info_kind = message.category_specific_info.WhichOneof("kind")
        category_specific_info: CategorySpecificInfo | None = None
        if category_specific_info_kind is not None:
            category_specific_info = CategorySpecificInfo(
                kind=category_specific_info_kind,
                fields=MessageToDict(
                    getattr(
                        message.category_specific_info, category_specific_info_kind
                    ),
                    always_print_fields_with_no_presence=True,
                    preserving_proto_field_name=True,
                ),
            )

        category_mismatched = False
        if (
            category_specific_info_kind
            and isinstance(category, ElectricalComponentCategory)
            and category.name.lower() != category_specific_info_kind
        ):
            category_mismatched = True

        return _ElectricalComponentBaseData(
            component_id,
            microgrid_id,
            message.name,
            message.model,
            category,
            lifetime,
            metric_config_bounds,
            category_specific_info,
            provides_telemetry,
            accepts_control,
            category_mismatched,
        )


# pylint: disable-next=too-many-locals,too-many-branches,too-many-return-statements
def electrical_component_from_proto(
    message: electrical_components_pb2.ElectricalComponent,
) -> ElectricalComponentTypes:
    """Convert a protobuf message to an electrical component instance.

    Malformed or forward-incompatible input is surfaced through the returned
    type rather than a side channel: an unspecified category yields an
    `UnspecifiedElectricalComponent`, an unrecognized one an
    `UnrecognizedElectricalComponent`, a category that disagrees with its
    carried info a `MismatchedCategoryElectricalComponent`, and an unspecified
    or unrecognized battery, EV charger or inverter type the matching
    `Unrecognized*` class (which preserves the raw wire `type`).

    Args:
        message: The protobuf message.

    Returns:
        The resulting electrical component instance.
    """
    with ignoring_deprecations():
        base_data = _electrical_component_base_from_proto(message)

        if base_data.category_mismatched:
            return MismatchedCategoryElectricalComponent(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                model=base_data.model,
                category=message.category,
                category_name=_category_name(message.category),
                operational_lifetime=base_data.lifetime,
                _provides_telemetry=base_data.provides_telemetry,
                _accepts_control=base_data.accepts_control,
                _allow_construction=True,
                category_specific_info=base_data.category_specific_info,
                metric_config_bounds=base_data.metric_config_bounds,
            )
        match base_data.category:
            case int():
                return UnrecognizedElectricalComponent(
                    id=base_data.component_id,
                    microgrid_id=base_data.microgrid_id,
                    name=base_data.name,
                    model=base_data.model,
                    category=message.category,
                    operational_lifetime=base_data.lifetime,
                    _provides_telemetry=base_data.provides_telemetry,
                    _accepts_control=base_data.accepts_control,
                    _allow_construction=True,
                    category_specific_info=base_data.category_specific_info,
                    metric_config_bounds=base_data.metric_config_bounds,
                )
            case (
                ElectricalComponentCategory.UNSPECIFIED
                | ElectricalComponentCategory.CHP
                | ElectricalComponentCategory.CONVERTER
                | ElectricalComponentCategory.CRYPTO_MINER
                | ElectricalComponentCategory.ELECTROLYZER
                | ElectricalComponentCategory.HVAC
                | ElectricalComponentCategory.METER
                | ElectricalComponentCategory.PRECHARGER
                | ElectricalComponentCategory.BREAKER
                | ElectricalComponentCategory.STEAM_BOILER
                | ElectricalComponentCategory.WIND_TURBINE
                | ElectricalComponentCategory.PLC
                | ElectricalComponentCategory.STATIC_TRANSFER_SWITCH
                | ElectricalComponentCategory.UNINTERRUPTIBLE_POWER_SUPPLY
                | ElectricalComponentCategory.CAPACITOR_BANK
            ):
                return _TRIVIAL_TYPELESS_CLASS_BY_PROTO_CATEGORY[
                    base_data.category.value
                ](
                    id=base_data.component_id,
                    microgrid_id=base_data.microgrid_id,
                    name=base_data.name,
                    model=base_data.model,
                    operational_lifetime=base_data.lifetime,
                    _provides_telemetry=base_data.provides_telemetry,
                    _accepts_control=base_data.accepts_control,
                    _allow_construction=True,
                    metric_config_bounds=base_data.metric_config_bounds,
                )
            case ElectricalComponentCategory.BATTERY:
                battery_info = _leftover_info(base_data.category_specific_info, "type")
                raw_battery_type = message.category_specific_info.battery.type
                battery_class = _BATTERY_CLASS_BY_PROTO_TYPE.get(raw_battery_type)
                if battery_class is None:
                    return UnrecognizedBattery(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        model=base_data.model,
                        operational_lifetime=base_data.lifetime,
                        _provides_telemetry=base_data.provides_telemetry,
                        _accepts_control=base_data.accepts_control,
                        _allow_construction=True,
                        category_specific_info=battery_info,
                        metric_config_bounds=base_data.metric_config_bounds,
                        type=raw_battery_type,
                    )
                return battery_class(
                    id=base_data.component_id,
                    microgrid_id=base_data.microgrid_id,
                    name=base_data.name,
                    model=base_data.model,
                    operational_lifetime=base_data.lifetime,
                    _provides_telemetry=base_data.provides_telemetry,
                    _accepts_control=base_data.accepts_control,
                    _allow_construction=True,
                    category_specific_info=battery_info,
                    metric_config_bounds=base_data.metric_config_bounds,
                )
            case ElectricalComponentCategory.EV_CHARGER:
                ev_charger_info = _leftover_info(
                    base_data.category_specific_info, "type"
                )
                raw_ev_charger_type = message.category_specific_info.ev_charger.type
                ev_charger_class = _EV_CHARGER_CLASS_BY_PROTO_TYPE.get(
                    raw_ev_charger_type
                )
                if ev_charger_class is None:
                    return UnrecognizedEvCharger(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        model=base_data.model,
                        operational_lifetime=base_data.lifetime,
                        _provides_telemetry=base_data.provides_telemetry,
                        _accepts_control=base_data.accepts_control,
                        _allow_construction=True,
                        category_specific_info=ev_charger_info,
                        metric_config_bounds=base_data.metric_config_bounds,
                        type=raw_ev_charger_type,
                    )
                return ev_charger_class(
                    id=base_data.component_id,
                    microgrid_id=base_data.microgrid_id,
                    name=base_data.name,
                    model=base_data.model,
                    operational_lifetime=base_data.lifetime,
                    _provides_telemetry=base_data.provides_telemetry,
                    _accepts_control=base_data.accepts_control,
                    _allow_construction=True,
                    category_specific_info=ev_charger_info,
                    metric_config_bounds=base_data.metric_config_bounds,
                )
            case ElectricalComponentCategory.GRID_CONNECTION_POINT:
                grid_info = _leftover_info(
                    base_data.category_specific_info, "rated_fuse_current"
                )
                rated_fuse_current = (
                    message.category_specific_info.grid_connection_point.rated_fuse_current
                )
                # No need to check for negatives because the protobuf type is uint32.
                return GridConnectionPoint(
                    id=base_data.component_id,
                    microgrid_id=base_data.microgrid_id,
                    name=base_data.name,
                    model=base_data.model,
                    operational_lifetime=base_data.lifetime,
                    _provides_telemetry=base_data.provides_telemetry,
                    _accepts_control=base_data.accepts_control,
                    _allow_construction=True,
                    category_specific_info=grid_info,
                    metric_config_bounds=base_data.metric_config_bounds,
                    rated_fuse_current=rated_fuse_current,
                )
            case ElectricalComponentCategory.INVERTER:
                inverter_info = _leftover_info(base_data.category_specific_info, "type")
                raw_inverter_type = message.category_specific_info.inverter.type
                inverter_class = _INVERTER_CLASS_BY_PROTO_TYPE.get(raw_inverter_type)
                if inverter_class is None:
                    return UnrecognizedInverter(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        model=base_data.model,
                        operational_lifetime=base_data.lifetime,
                        _provides_telemetry=base_data.provides_telemetry,
                        _accepts_control=base_data.accepts_control,
                        _allow_construction=True,
                        category_specific_info=inverter_info,
                        metric_config_bounds=base_data.metric_config_bounds,
                        type=raw_inverter_type,
                    )
                return inverter_class(
                    id=base_data.component_id,
                    microgrid_id=base_data.microgrid_id,
                    name=base_data.name,
                    model=base_data.model,
                    operational_lifetime=base_data.lifetime,
                    _provides_telemetry=base_data.provides_telemetry,
                    _accepts_control=base_data.accepts_control,
                    _allow_construction=True,
                    category_specific_info=inverter_info,
                    metric_config_bounds=base_data.metric_config_bounds,
                )
            case ElectricalComponentCategory.POWER_TRANSFORMER:
                power_transformer_info = _leftover_info(
                    base_data.category_specific_info, "primary", "secondary"
                )
                return PowerTransformer(
                    id=base_data.component_id,
                    microgrid_id=base_data.microgrid_id,
                    name=base_data.name,
                    model=base_data.model,
                    operational_lifetime=base_data.lifetime,
                    _provides_telemetry=base_data.provides_telemetry,
                    _accepts_control=base_data.accepts_control,
                    _allow_construction=True,
                    category_specific_info=power_transformer_info,
                    metric_config_bounds=base_data.metric_config_bounds,
                    primary_voltage=message.category_specific_info.power_transformer.primary,
                    secondary_voltage=message.category_specific_info.power_transformer.secondary,
                )
            case unexpected_category:
                assert_never(unexpected_category)


def _metric_config_bounds_from_proto(
    message: Sequence[electrical_components_pb2.MetricConfigBounds],
) -> dict[Metric | int, BoundsSet | InvalidBoundsSet]:
    """Convert `MetricConfigBounds` messages to a mapping of metric to bounds set.

    The keys of the result map are
    [`Metric`][frequenz.client.common.metrics.Metric] enum members (or `int` for
    unrecognized values, and `0` for the unspecified metric). Each value
    aggregates *every* entry that named the metric into a single set: a
    [`BoundsSet`][frequenz.client.common.metrics.BoundsSet] (their union) when
    all of the metric's `config_bounds` are well-formed, or an
    [`InvalidBoundsSet`][frequenz.client.common.metrics.InvalidBoundsSet]
    preserving all the raw bounds in wire order when any is malformed.

    An entry with no configured limits — its `config_bounds` submessage absent,
    or present but empty — contributes an unbounded `Bounds()` (a `Bounds` with
    neither `lower` nor `upper` set imposes no limit in either direction), which
    normalizes into the empty, unbounded
    [`BoundsSet`][frequenz.client.common.metrics.BoundsSet]. Absence and a
    present-but-empty submessage are intentionally treated the same.

    Args:
        message: The `MetricConfigBounds` messages.

    Returns:
        A mapping from each metric to the set of its configured bounds.
    """
    grouped: dict[Metric | int, list[bounds_pb2.Bounds]] = {}
    for metric_bound in message:
        with ignoring_deprecations():
            metric = enum_from_proto(metric_bound.metric, Metric)
            if metric is Metric.UNSPECIFIED:
                metric = metric.value

        grouped.setdefault(metric, []).append(metric_bound.config_bounds)

    return {
        metric: bounds_set_from_proto(configs) for metric, configs in grouped.items()
    }


def _get_operational_lifetime_from_proto(
    message: electrical_components_pb2.ElectricalComponent,
) -> Lifetime | InvalidLifetime:
    """Get the operational lifetime from a protobuf message.

    Args:
        message: The protobuf message to extract the operational lifetime from.

    Returns:
        The extracted operational lifetime, an invalid lifetime preserving
            malformed timestamp ordering or a timestamp Python cannot
            represent, or an unbounded lifetime if the field is missing.
    """
    if message.HasField("operational_lifetime"):
        return lifetime_from_proto(message.operational_lifetime)
    return Lifetime()
